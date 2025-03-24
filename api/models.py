"""
Data Models for Tax Calculation

This module defines the data models used for tax calculation input validation and processing.
It uses Pydantic for data validation and type checking.

Key Models:
- TaxInput: Comprehensive model for tax calculation inputs including income, deductions,
           and various tax-saving investments.

The models include validation rules to ensure data integrity and proper tax calculations.
"""

from decimal import Decimal
from pydantic import BaseModel, validator, EmailStr, Field

class TaxInput(BaseModel):
    """
    Comprehensive model for tax calculation inputs.
    
    This model validates and stores all necessary information for calculating taxes
    under both old and new regimes.
    
    Attributes:
        income (Decimal): Total annual income
        age (int): Age of the taxpayer
        gender (str): Gender of the taxpayer
        city (str): City of residence (affects HRA calculations)
        rent (Decimal): Monthly rent paid
        has_hra (bool): Whether HRA is received from employer
        basic_salary (Decimal): Basic salary component
        email (EmailStr): Email address for sending tax report
    """
    # Personal Information
    email: EmailStr = Field(None, description="Email address for sending tax report")
    income: Decimal
    age: int
    gender: str
    city: str = "metro"
    
    # Income Details
    basic_salary: Decimal
    has_hra: bool = False
    rent: Decimal = Decimal('0')
    
    # Investment Details
    section_80c: Decimal = Decimal('0')
    nps_contribution: Decimal = Decimal('0')
    health_insurance_premium: Decimal = Decimal('0')
    
    # Loan Details
    student_loan_interest: Decimal = Decimal('0')
    housing_loan_interest: Decimal = Decimal('0')
    housing_loan_principal: Decimal = Decimal('0')
    
    # Assessment Year
    assessment_year: str = "2024-25"

    @validator('age')
    def validate_age(cls, v):
        """Validate age is within reasonable range."""
        if v < 0 or v > 120:
            raise ValueError('Age must be between 0 and 120')
        return v

    @validator('gender')
    def validate_gender(cls, v):
        """Validate gender is one of the accepted values."""
        valid_genders = {'male', 'female', 'other'}
        if v.lower() not in valid_genders:
            raise ValueError('Gender must be one of: male, female, other')
        return v.lower()

    @validator('city')
    def validate_city(cls, v):
        """Validate city type for HRA calculation."""
        valid_cities = {'metro', 'non-metro'}
        if v.lower() not in valid_cities:
            raise ValueError('City must be either metro or non-metro')
        return v.lower()

    @validator('income', 'basic_salary', 'rent', 'section_80c', 
              'nps_contribution', 'health_insurance_premium',
              'student_loan_interest', 'housing_loan_interest',
              'housing_loan_principal')
    def validate_decimal(cls, v):
        """Validate decimal values are non-negative."""
        if v < 0:
            raise ValueError('Amount cannot be negative')
        return v

    @validator('assessment_year')
    def validate_assessment_year(cls, v):
        """Validate assessment year format."""
        if not v.match(r'^\d{4}-\d{2}$'):
            raise ValueError('Assessment year must be in format YYYY-YY')
        return v