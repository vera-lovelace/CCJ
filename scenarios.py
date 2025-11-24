"""
Scenario Management
Handles alternative calculation scenarios and component selection
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json

from mvpf_calculator import MVPFCalculator


class ScenarioManager:
    """
    Manages scenario definitions from alternative_calculations.json.

    Each scenario defines which subcomponents to include in calculations.
    """

    def __init__(self, scenarios_path=None, subcomponent_registry=None):
        """
        Initialize scenario manager.

        Args:
            scenarios_path (str): Path to alternative_calculations.json
            subcomponent_registry: Registry object to get all available subcomponents
        """
        self.scenarios = self._load_scenarios(scenarios_path)
        self._build_defaults(subcomponent_registry)

    def _load_scenarios(self, path):
        """Load scenarios from JSON file."""
        if path is None:
            path = os.path.join(os.path.dirname(__file__), 'Data', 'alternative_calculations.json')

        try:
            with open(path, 'r') as f:
                scenarios = json.load(f)
                print(f"✓ Loaded {len(scenarios)} scenarios")
                return scenarios
        except FileNotFoundError:
            print(f"Warning: {path} not found, using defaults")
            return {}

    def _build_defaults(self, registry):
        """Build default 'baseline' scenario with all subcomponents."""
        if registry is None or 'baseline' in self.scenarios:
            return

        # Group all subcomponents by component type
        components = {}
        for row_var, data in registry.data.items():
            comp = data['component']
            if comp not in components:
                components[comp] = []
            components[comp].append(row_var)

        self.scenarios['baseline'] = components

    def get_subcomponents(self, scenario, component):
        """
        Get list of subcomponents for a scenario and component.

        Args:
            scenario (str): Scenario name
            component (str): Component name ('detainee_values', 'society_values', 'govt_cost')

        Returns:
            list: Row_var names to include in calculation
        """
        if scenario not in self.scenarios:
            print(f"Warning: Scenario '{scenario}' not found, using all subcomponents")
            # Return empty list - let caller handle fallback
            return []

        return self.scenarios[scenario].get(component, [])

    def list_scenarios(self):
        """Get list of all available scenario names."""
        return list(self.scenarios.keys())

    def get_scenario_info(self, scenario):
        """
        Get full information about a scenario.

        Returns:
            dict: Scenario definition
        """
        return self.scenarios.get(scenario, {})

    def scenario_exists(self, scenario):
        """Check if a scenario exists."""
        return scenario in self.scenarios

    def add_scenario(self, name, definition):
        """
        Add or update a scenario (for runtime customization).

        Args:
            name (str): Scenario name
            definition (dict): Scenario definition with component lists
        """
        self.scenarios[name] = definition
        print(f"✓ Added/updated scenario: {name}")

    def get_subcomponent_count(self, scenario):
        """
        Get count of subcomponents in each component for a scenario.

        Returns:
            dict: {'detainee_values': int, 'society_values': int, 'govt_cost': int}
        """
        if scenario not in self.scenarios:
            return {}

        return {
            component: len(subcomps)
            for component, subcomps in self.scenarios[scenario].items()
        }


@dataclass
class ScenarioDefinition:
    """
    Complete definition of an MVPF calculation scenario.

    Combines:
    - Which subcomponents to include
    - What parameter values to use
    - Metadata for documentation
    """
    name: str
    key: str
    description: str

    # Subcomponents to include
    detainee_values: List[str] = field(default_factory=list)
    society_values: List[str] = field(default_factory=list)
    govt_cost: List[str] = field(default_factory=list)

    # Parameter configuration
    parameter_preset: Optional[str] = 'baseline'
    parameter_overrides: Dict[str, float] = field(default_factory=dict)

    # Metadata
    tags: List[str] = field(default_factory=list)
    author: Optional[str] = None
    created_date: Optional[str] = None

    def get_all_subcomponents(self) -> Dict[str, List[str]]:
        """Get subcomponents organized by component type."""
        return {
            'detainee_values': self.detainee_values,
            'society_values': self.society_values,
            'govt_cost': self.govt_cost
        }

    def get_parameters(self, preset_registry=None) -> Dict[str, float]:
        """
        Get complete parameter configuration for this scenario.

        Starts with preset, then applies overrides.
        """
        from parameters import ParameterPresets

        # Start with preset
        if self.parameter_preset:
            params = ParameterPresets.get_preset(self.parameter_preset)
        else:
            params = {}

        # Apply overrides
        params.update(self.parameter_overrides)

        return params

    def total_subcomponents(self) -> int:
        """Count total subcomponents across all categories."""
        return (len(self.detainee_values) +
                len(self.society_values) +
                len(self.govt_cost))

    @classmethod
    def from_dict(cls, key: str, data: dict) -> 'ScenarioDefinition':
        """Create ScenarioDefinition from JSON dict."""
        return cls(
            key=key,
            name=data.get('name', key),
            description=data.get('description', ''),
            detainee_values=data.get('subcomponents', {}).get('detainee_values', []),
            society_values=data.get('subcomponents', {}).get('society_values', []),
            govt_cost=data.get('subcomponents', {}).get('govt_cost', []),
            parameter_preset=data.get('default_parameters', 'baseline'),
            parameter_overrides=data.get('parameter_overrides', {}),
            tags=data.get('tags', []),
            author=data.get('author'),
            created_date=data.get('created_date')
        )

    def to_dict(self) -> dict:
        """Export to JSON-compatible dict."""
        return {
            'name': self.name,
            'description': self.description,
            'subcomponents': {
                'detainee_values': self.detainee_values,
                'society_values': self.society_values,
                'govt_cost': self.govt_cost
            },
            'default_parameters': self.parameter_preset,
            'parameter_overrides': self.parameter_overrides,
            'tags': self.tags,
            'author': self.author,
            'created_date': self.created_date
        }


class EnhancedScenarioManager:
    """
    Enhanced scenario manager with parameter integration.
    """

    def __init__(self, scenarios_path='Data/alternative_calculations.json'):
        self.scenarios: Dict[str, ScenarioDefinition] = {}
        self._load_scenarios(scenarios_path)

    def _load_scenarios(self, path):
        """Load scenarios from JSON."""
        try:
            with open(path, 'r') as f:
                data = json.load(f)

            for key, scenario_data in data.items():
                # Handle both old and new format
                if 'name' in scenario_data:
                    # New format with metadata
                    self.scenarios[key] = ScenarioDefinition.from_dict(key, scenario_data)
                else:
                    # Old format (just lists of subcomponents)
                    self.scenarios[key] = ScenarioDefinition(
                        key=key,
                        name=key.replace('_', ' ').title(),
                        description=f"Scenario: {key}",
                        detainee_values=scenario_data.get('detainee_values', []),
                        society_values=scenario_data.get('society_values', []),
                        govt_cost=scenario_data.get('govt_cost', [])
                    )

            print(f"✓ Loaded {len(self.scenarios)} scenarios")
        except FileNotFoundError:
            print(f"⚠️ {path} not found")

    def get_scenario(self, key: str) -> ScenarioDefinition:
        """Get scenario definition."""
        if key not in self.scenarios:
            raise KeyError(f"Scenario '{key}' not found. Available: {self.list_scenarios()}")
        return self.scenarios[key]

    def list_scenarios(self) -> List[str]:
        """Get list of scenario keys."""
        return list(self.scenarios.keys())

    def get_scenarios_by_tag(self, tag: str) -> List[ScenarioDefinition]:
        """Find scenarios by tag."""
        return [s for s in self.scenarios.values() if tag in s.tags]

    def add_scenario(self, scenario: ScenarioDefinition):
        """Add new scenario."""
        self.scenarios[scenario.key] = scenario
        print(f"✓ Added scenario: {scenario.name}")

    def export_to_json(self, path='Data/alternative_calculations.json'):
        """Export all scenarios to JSON."""
        data = {key: s.to_dict() for key, s in self.scenarios.items()}
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Exported {len(self.scenarios)} scenarios to {path}")


