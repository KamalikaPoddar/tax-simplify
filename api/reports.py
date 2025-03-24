"""
Tax Report Generation Module

This module handles the generation of detailed tax reports in various formats.
Currently supports CSV format reports with deduction breakdowns and optimization
suggestions.

Features:
- CSV report generation with detailed deduction breakdown
- Tax optimization suggestions
- Structured report format with sections
- Support for various data types and formatting
"""

from typing import Dict, Any, List
import csv
from io import StringIO

def generate_tax_report_csv(
    deduction_breakdown: Dict[str, Any],
    optimization_suggestions: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Generate a detailed tax report in CSV format.
    
    Creates a comprehensive tax report containing deduction breakdowns and
    optimization suggestions in CSV format. The report is structured with
    clear sections and formatted data.
    
    Args:
        deduction_breakdown (Dict[str, Any]): Breakdown of all deductions
            Each deduction should have:
            - used: Amount utilized
            - limit: Maximum allowed amount
            - remaining_capacity: Available unused amount
            - estimated_tax_saving_if_fully_used: Potential tax saving
            - tax_saved_from_used_approx: Actual tax saved
        
        optimization_suggestions (List[Dict[str, Any]]): List of tax optimization tips
            Each suggestion should have:
            - deduction: Name of the deduction
            - current_investment: Current amount invested
            - recommended_investment: Suggested investment
            - potential_tax_saving: Possible tax saving
            - action: Recommended action
    
    Returns:
        Dict[str, Any]: Dictionary containing:
            - file_data (bytes): The CSV report content
            - filename (str): Suggested filename for the report
            - content_type (str): MIME type for the file
    
    Example:
        >>> report = generate_tax_report_csv(
        ...     deduction_breakdown={
        ...         '80C': {
        ...             'used': '150000',
        ...             'limit': '150000',
        ...             'remaining_capacity': '0',
        ...             'estimated_tax_saving_if_fully_used': '45000',
        ...             'tax_saved_from_used_approx': '45000'
        ...         }
        ...     },
        ...     optimization_suggestions=[
        ...         {
        ...             'deduction': '80D',
        ...             'current_investment': '0',
        ...             'recommended_investment': '25000',
        ...             'potential_tax_saving': '7500',
        ...             'action': 'Consider health insurance investment'
        ...         }
        ...     ]
        ... )
        >>> assert report['content_type'] == 'text/csv'
    """
    output = StringIO()
    writer = csv.writer(output)

    # Write Header
    writer.writerow(['Deduction Section', 'Used Amount', 'Limit', 'Remaining Capacity', 'Estimated Tax Saving (Full Use)', 'Tax Saved (Used Approx.)'])

    # Write Deduction Breakdown Data
    for section, data in deduction_breakdown.items():
        writer.writerow([
            section,
            data.get('used', 'N/A'),
            data.get('limit', 'N/A'),
            data.get('remaining_capacity', 'N/A'),
            data.get('estimated_tax_saving_if_fully_used', 'N/A'),
            data.get('tax_saved_from_used_approx', 'N/A')
        ])

    writer.writerow([])  # Add an empty row for spacing
    writer.writerow(['Optimization Suggestions'])
    writer.writerow(['Deduction', 'Current Investment', 'Recommended Investment', 'Potential Tax Saving', 'Action'])

    # Write Optimization Suggestions Data
    for suggestion in optimization_suggestions:
        writer.writerow([
            suggestion.get('deduction', 'N/A'),
            suggestion.get('current_investment', 'N/A'),
            suggestion.get('recommended_investment', 'N/A'),
            suggestion.get('potential_tax_saving', 'N/A'),
            suggestion.get('action', 'N/A')
        ])

    csv_report = output.getvalue().encode('utf-8')
    return {
        'file_data': csv_report,
        'filename': 'tax_report.csv',
        'content_type': 'text/csv'
    }