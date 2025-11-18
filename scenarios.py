"""
Scenario Management
Handles alternative calculation scenarios and component selection
"""

import json
import os

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