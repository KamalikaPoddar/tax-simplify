"""
Tax Savvy Calculator API - Main Application Module

This module serves as the main entry point for the Tax Savvy Calculator API.
It provides endpoints for tax calculation, report generation, and report downloading.
"""

from datetime import datetime, date
from decimal import Decimal
import json
import logging
import re
from http import HTTPStatus
from functools import wraps
import decimal
from typing import Optional, List, Dict, Any, Union, Tuple

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from pydantic import ValidationError, EmailStr

from .config import Config
from .security import (
    require_api_key,
    validate_content_length,
    sanitize_input,
    add_security_headers,
    create_jwt_token
)
from .tax_slabs_data import load_tax_slabs, TaxDataNotFoundError, InvalidTaxSlabsStructureError
from .tax_calculations import calculate_old_regime_tax, calculate_new_regime_tax
from .tax_utils import calculate_age
from .optimization import generate_optimization_suggestions
from .models import TaxInput
from .email_utils import send_email_with_attachment
from .reports import generate_tax_report_csv

# Initialize Flask app with security configurations
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
app.secret_key = Config.SECRET_KEY

# Configure CORS with specific origins
CORS(app, resources={
    r"/api/*": {
        "origins": Config.ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "X-API-Key", "Authorization"]
    }
})

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[f"{Config.RATE_LIMIT_PER_MINUTE} per minute"]
)

# Configure logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.before_request
def before_request():
    """Pre-request processing."""
    if request.is_json:
        data = request.get_json()
        sanitized_data = sanitize_input(data)
        logger.info(f"Request data (sanitized): {sanitized_data}")

@app.after_request
def after_request(response: Response) -> Response:
    """Post-request processing."""
    return add_security_headers(response)

@app.route('/api/calculateTax', methods=['POST'])
@limiter.limit(f"{Config.RATE_LIMIT_PER_MINUTE} per minute")
@require_api_key
@validate_content_length
def calculate_tax_api():
    """Calculate tax for both old and new regimes and email report."""
    try:
        # Validate and sanitize input
        data = request.get_json()
        sanitized_data = sanitize_input(data)
        tax_input = TaxInput(**sanitized_data)
        
        # Load tax configuration
        tax_data = load_tax_slabs()
        
        # Calculate taxes for both regimes
        old_tax, old_ti, old_breakdown = calculate_old_regime_tax(
            input_data=tax_input,
            tax_data=tax_data
        )
        
        new_tax, new_ti = calculate_new_regime_tax(
            income=tax_input.income,
            gender=tax_input.gender,
            basic_salary=tax_input.basic_salary,
            assessment_year=tax_input.assessment_year
        )
        
        # Generate optimization suggestions
        optimization_suggestions = generate_optimization_suggestions(
            tax_input, 
            old_breakdown,
            tax_input.assessment_year,
            tax_input.age,
            tax_data
        )
        
        # Determine optimal regime
        total_potential_tax_saving = sum(
            Decimal(str(val.get('estimated_tax_saving_if_fully_used', 0)))
            for val in old_breakdown.values()
            if isinstance(val.get('estimated_tax_saving_if_fully_used'), (int, float, str))
        )
        optimal_old_tax = (old_tax - total_potential_tax_saving).quantize(Decimal("0.01"))
        optimal_regime = "old_regime" if optimal_old_tax < new_tax else "new_regime"
        
        # Prepare response
        result = {
            'status': 'success',
            'optimal_regime': optimal_regime,
            'old_regime': {
                'tax': str(old_tax),
                'taxable_income': str(old_ti),
                'deduction_breakdown': old_breakdown
            },
            'new_regime': {
                'tax': str(new_tax),
                'taxable_income': str(new_ti)
            },
            'optimization_suggestions': optimization_suggestions
        }
        
        # Generate and send report if email is provided
        if tax_input.email:
            try:
                report_csv = generate_tax_report_csv(old_breakdown, optimization_suggestions)
                email_sent = send_email_with_attachment(
                    to_email=tax_input.email,
                    subject='Your Tax Calculation Report',
                    body='Please find attached your detailed tax calculation report.',
                    attachment_name='tax_report.csv',
                    attachment_content=report_csv['file_data']
                )
                result['report_emailed'] = email_sent
                if email_sent:
                    logger.info(f"Tax report email sent successfully to {tax_input.email}")
                else:
                    logger.warning(f"Failed to send tax report email to {tax_input.email}")
            except Exception as e:
                logger.error(f"Error sending email: {str(e)}")
                result['report_emailed'] = False
                result['email_error'] = "Failed to send email report"
        
        return jsonify(result)
        
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            'error': 'Invalid input data',
            'details': str(e)
        }), HTTPStatus.BAD_REQUEST
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/api/tax/download-report', methods=['POST'])
def download_tax_report():
    """Download tax report endpoint"""
    try:
        data = request.get_json()
        if not data or 'tax_data' not in data:
            return jsonify({'error': 'Invalid request data'}), 400

        tax_data = data['tax_data']
        if not isinstance(tax_data, dict) or 'old_regime' not in tax_data:
            return jsonify({'error': 'Invalid tax data format'}), 400

        # Generate the report
        if generate_tax_report_csv:
            try:
                report_data = generate_tax_report_csv(tax_data['old_regime']['deduction_breakdown'])
                return Response(
                    report_data['file_data'],
                    mimetype=report_data['content_type'],
                    headers={
                        'Content-Disposition': f'attachment; filename={report_data["filename"]}'
                    }
                )
            except Exception as e:
                logger.error(f"Error generating report: {str(e)}")
                return jsonify({'error': f'Failed to generate report: {str(e)}'}), 500
        else:
            return jsonify({"Warning": "Report generation is disabled, no report is sent"}), 200

    except Exception as e:
        logger.error(f"Error in download_tax_report: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)