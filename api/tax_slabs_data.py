"""
Tax Slabs and Configuration Data Module

This module handles loading and managing tax slab configurations and related data
from a JSON configuration file. It provides access to various tax-related data
such as tax slabs, surcharge rates, rebates, and deduction limits.

Features:
- Dynamic loading of tax configurations from JSON
- Support for multiple assessment years
- Age-based tax slab selection
- Regime-specific configurations (old vs new)
- Secure error handling with custom exceptions

Configuration File Structure:
The module expects a tax_slabs.json file with the following structure:
{
    "2023-24": {
        "old_regime": {
            "general": [...],
            "senior_citizen": [...],
            "super_senior_citizen": [...]
        },
        "new_regime": {
            "general": [...]
        },
        "surcharge": {...},
        "rebate_87A": {...},
        "standard_deduction": 50000,
        "section_80d_limits": {
            "general": {...},
            "senior_citizen": {...}
        }
    }
}
"""

import json
import logging
from decimal import Decimal
from typing import List, Dict, Union, Optional, Any

# Custom Exceptions (Move these to tax_slabs_data.py as they are related to data loading)
class TaxDataNotFoundError(Exception):
    """
    Exception raised when tax configuration data cannot be found.
    
    This exception is raised in situations where:
    - The tax_slabs.json file is missing
    - The file cannot be accessed due to permissions
    - Required data is missing from the configuration
    """
    pass

class InvalidTaxSlabsStructureError(Exception):
    """
    Exception raised when tax slabs data has invalid structure.
    
    This exception is raised when:
    - The JSON file is malformed
    - Required fields are missing
    - Data types are incorrect
    - Slab ranges are invalid or overlapping
    """
    pass

logger = logging.getLogger(__name__)  # Get logger for this module

def load_tax_slabs() -> Dict[str, Any]:
    """
    Load tax slabs and configurations from tax_slabs.json.
    
    Reads and parses the tax configuration file, performing basic validation
    of the data structure.
    
    Returns:
        Dict[str, Any]: Complete tax configuration data
    
    Raises:
        TaxDataNotFoundError: If configuration file is missing
        InvalidTaxSlabsStructureError: If JSON structure is invalid
    """
    try:
        with open('tax_slabs.json', 'r') as f:
            tax_data = json.load(f)
        return tax_data
    except FileNotFoundError:
        logger.error("Tax slabs file 'tax_slabs.json' not found.")
        raise TaxDataNotFoundError("Tax configuration file not found.")
    except json.JSONDecodeError:
        logger.error("Error decoding JSON from 'tax_slabs.json'.")
        raise InvalidTaxSlabsStructureError("Invalid JSON format in tax configuration file.")
    except Exception as e:
        logger.error(f"Unexpected error loading tax slabs: {e}")
        raise TaxDataNotFoundError(f"Failed to load tax configuration: {e}")


def get_tax_slabs(
    assessment_year: str,
    regime_type: str,
    age: Optional[int] = None
) -> List[Dict[str, Union[float, int, Decimal, None]]]:
    """
    Retrieve appropriate tax slabs based on assessment year, regime type, and age.
    
    Selects the correct tax slab configuration based on the provided parameters,
    taking into account special rates for senior citizens in the old regime.
    
    Args:
        assessment_year (str): Assessment year in format 'YYYY-YY'
        regime_type (str): Either 'old' or 'new_regime'
        age (Optional[int]): Age of taxpayer, used for senior citizen slabs
    
    Returns:
        List[Dict[str, Union[float, int, Decimal, None]]]: List of tax slabs
            Each slab contains:
            - limit: Upper limit of the slab (None for highest slab)
            - rate: Tax rate as decimal (e.g., 0.05 for 5%)
    
    Example:
        >>> slabs = get_tax_slabs('2023-24', 'old', 65)
        >>> # Returns senior citizen slabs for old regime
    """
    tax_data = load_tax_slabs()
    year_data = tax_data.get(assessment_year, {})
    regime_data = year_data.get(f"{regime_type}_regime", {})

    if regime_type == 'old':
        if age is not None:
            if age > 80:
                return regime_data.get('super_senior_citizen', [])
            elif age >= 60:
                return regime_data.get('senior_citizen', [])
        return regime_data.get('general', [])
    elif regime_type == 'new_regime':
        return regime_data.get('general', [])
    return []


def get_surcharge_rates(assessment_year: str) -> Dict[str, float]:
    """
    Retrieve surcharge rates for a given assessment year.
    
    Gets the applicable surcharge rates for different income levels.
    
    Args:
        assessment_year (str): Assessment year in format 'YYYY-YY'
    
    Returns:
        Dict[str, float]: Dictionary mapping income thresholds to surcharge rates
    
    Example:
        >>> rates = get_surcharge_rates('2023-24')
        >>> # Returns something like:
        >>> # {'50L': 0.10, '1Cr': 0.15, '2Cr': 0.25}
    """
    tax_data = load_tax_slabs()
    year_data = tax_data.get(assessment_year, {})
    regime_data = year_data.get('old_regime', {}) # Assuming surcharge is same for old and new, adjust if needed
    return regime_data.get('surcharge', {})


def get_rebate_87a(assessment_year: str) -> Optional[Dict[str, Union[str, int]]]:
    """
    Retrieve rebate details under section 87A for a given assessment year.
    
    Gets the maximum rebate amount and income limit for section 87A relief.
    
    Args:
        assessment_year (str): Assessment year in format 'YYYY-YY'
    
    Returns:
        Optional[Dict[str, Union[str, int]]]: Dictionary containing:
            - max_rebate: Maximum rebate amount
            - income_limit: Income limit for eligibility
            Returns None if no rebate configured for the year
    """
    tax_data = load_tax_slabs()
    year_data = tax_data.get(assessment_year, {})
    return year_data.get('rebate_87A')


def get_standard_deduction(assessment_year: str) -> Optional[int]:
    """
    Retrieve standard deduction amount for a given assessment year.
    
    Gets the standard deduction amount applicable for salaried individuals.
    
    Args:
        assessment_year (str): Assessment year in format 'YYYY-YY'
    
    Returns:
        Optional[int]: Standard deduction amount, None if not configured
    """
    tax_data = load_tax_slabs()
    year_data = tax_data.get(assessment_year, {})
    return year_data.get('standard_deduction')

def get_80D_limits(assessment_year: str, age: int) -> Optional[Dict[str, int]]:
    """
    Retrieve section 80D deduction limits based on assessment year and age.
    
    Gets the applicable health insurance premium deduction limits under
    section 80D, considering age-based categories.
    
    Args:
        assessment_year (str): Assessment year in format 'YYYY-YY'
        age (int): Age of the taxpayer
    
    Returns:
        Optional[Dict[str, int]]: Dictionary containing:
            - self: Limit for self and family
            - parents: Additional limit for parents
            Returns None if limits not configured
    
    Example:
        >>> limits = get_80D_limits('2023-24', 65)
        >>> # Returns senior citizen limits
        >>> # {'self': 50000, 'parents': 50000}
    """
    tax_data = load_tax_slabs()
    year_data = tax_data.get(assessment_year, {})
    limits_80d = year_data.get('section_80d_limits', {})

    if age >= 60:
        return limits_80d.get('senior_citizen')
    else:
        return limits_80d.get('general')