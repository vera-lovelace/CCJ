"""
  CPI Adjustment Module
  Single source of truth for inflation adjustments
"""
import os
import pandas as pd
from typing import Dict, Tuple

class CPIAdjuster:
      """
      Handles CPI-based inflation adjustments.
      
      Optimized for:
      - Fast lookups (pre-computed factors to 2025)
      - Flexible adjustments (any year to any year)
      - Caching for repeated calculations
      """

      def __init__(self, data_dir='Data', target_year=2025):
          """
          Initialize CPI adjuster with data directory.
          
          Args:
              data_dir: Directory containing CPI.csv
              target_year: Default target year for adjustments (default: 2025)
          """
          self.target_year = target_year
          self.data_dir = data_dir

          # Load CPI data
          cpi_path = os.path.join(data_dir, 'CPI.csv')
          self.cpi_df = pd.read_csv(cpi_path)

          # Build fast lookup structures
          self.cpi_annual = dict(zip(self.cpi_df['year'],
                                     self.cpi_df['cpi_annual']))
          self.factor_to_2025 = dict(zip(self.cpi_df['year'],
                                         self.cpi_df['factor_to_2025']))

          # Cache for custom calculations
          self._cache: Dict[Tuple, float] = {}

          print(f"✓ CPIAdjuster loaded: {len(self.cpi_df)} years "
                f"({self.year_range[0]}-{self.year_range[1]})")

      @property
      def year_range(self) -> Tuple[int, int]:
          """Get (min_year, max_year) available in data."""
          years = sorted(self.cpi_annual.keys())
          return (years[0], years[-1]) if years else (None, None)

      @property
      def available_years(self) -> list:
          """Get list of all available years."""
          return sorted(self.cpi_annual.keys())

      def adjust(self, value: float, from_year: int) -> float:
          """
          Adjust value from source year to default target year (2025).

          Fast path - uses pre-computed factors with caching.

          Args:
              value: Amount in source year dollars
              from_year: Source year

          Returns:
              Value adjusted to target year
          """
          # Check cache first
          cache_key = (value, from_year, self.target_year)
          if cache_key in self._cache:
              return self._cache[cache_key]

          if from_year not in self.factor_to_2025:
              raise ValueError(
                  f"No CPI data for year {from_year}. "
                  f"Available: {self.year_range[0]}-{self.year_range[1]}"
              )

          adjusted = value * self.factor_to_2025[from_year]

          # Cache result
          self._cache[cache_key] = adjusted
          return adjusted

      def adjust_to_year(self, value: float, from_year: int, to_year: int) -> float:
          """
          Adjust value from source year to any target year.
          
          Flexible path - calculates ratio. Results cached.
          
          Args:
              value: Amount in source year dollars
              from_year: Source year
              to_year: Target year
              
          Returns:
              Value adjusted to target year
          """
          # Fast path for same year
          if from_year == to_year:
              return value

          # Fast path for target year = 2025
          if to_year == self.target_year:
              return self.adjust(value, from_year)

          # Check cache
          cache_key = (value, from_year, to_year)
          if cache_key in self._cache:
              return self._cache[cache_key]

          # Validate years
          if from_year not in self.cpi_annual:
              raise ValueError(f"No CPI data for source year {from_year}")
          if to_year not in self.cpi_annual:
              raise ValueError(f"No CPI data for target year {to_year}")

          # Calculate using CPI annual values
          cpi_from = self.cpi_annual[from_year]
          cpi_to = self.cpi_annual[to_year]

          adjusted = value * (cpi_to / cpi_from)

          # Cache and return
          self._cache[cache_key] = adjusted
          return adjusted

      def get_factor(self, from_year: int, to_year: int = None) -> float:
          """
          Get inflation factor without applying to a value.
          
          Args:
              from_year: Source year
              to_year: Target year (default: 2025)
              
          Returns:
              Multiplication factor
          """
          if to_year is None:
              to_year = self.target_year

          if from_year == to_year:
              return 1.0

          # Fast path
          if to_year == 2025:
              return self.factor_to_2025[from_year]

          # Calculate ratio
          return self.cpi_annual[to_year] / self.cpi_annual[from_year]

      def clear_cache(self):
          """Clear the adjustment cache."""
          self._cache.clear()

      def validate_year(self, year: int) -> bool:
          """Check if year exists in CPI data."""
          return year in self.cpi_annual
