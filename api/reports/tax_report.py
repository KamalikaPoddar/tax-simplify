import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
import os
from typing import Dict, Any
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_tax_report(tax_data: Dict[str, Any], email: str) -> None:
    """
    Generate an Excel report from tax data and email it to the user.
    
    Args:
        tax_data: Dictionary containing tax deduction details
        email: Email address to send the report to
    """
    try:
        # Create DataFrame for the report
        report_data = []
        for category, details in tax_data.items():
            report_data.append({
                'Category': category,
                'Amount Used': details['used'],
                'Maximum Limit': details['limit'],
                'Remaining Capacity': details['remaining_capacity'],
                'Potential Tax Savings': details['estimated_tax_saving_if_fully_used'],
                'Current Tax Savings': details['tax_saved_from_used_approx']
            })
        
        df = pd.DataFrame(report_data)
        
        # Generate timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tax_report_{timestamp}.xlsx"
        
        try:
            # Create Excel writer with formatting
            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            df.to_excel(writer, sheet_name='Tax Deductions', index=False)
            
            # Get workbook and worksheet objects for formatting
            workbook = writer.book
            worksheet = writer.sheets['Tax Deductions']
            
            # Add formatting
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#D3D3D3',
                'border': 1
            })
            
            # Format headers
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # Adjust column widths
            for i, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).apply(len).max(), len(col)) + 2
                worksheet.set_column(i, i, max_length)
            
            writer.close()
            logger.info(f"Excel report generated: {filename}")
            
        except Exception as e:
            logger.error(f"Error generating Excel file: {str(e)}")
            raise
        
        try:
            # Email configuration
            sender_email = os.environ.get('EMAIL_SENDER')
            sender_password = os.environ.get('EMAIL_PASSWORD')
            smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.environ.get('SMTP_PORT', '587'))
            
            if not all([sender_email, sender_password]):
                raise ValueError("Email credentials not configured. Please check environment variables.")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = 'Your Tax Deduction Report'
            
            body = """
            Dear User,
            
            Please find attached your tax deduction report. This report provides a detailed 
            breakdown of your tax deductions and potential savings.
            
            Best regards,
            Tax Calculator Team
            """
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach Excel file
            with open(filename, 'rb') as f:
                attachment = MIMEApplication(f.read(), _subtype='xlsx')
                attachment.add_header('Content-Disposition', 'attachment', filename=filename)
                msg.attach(attachment)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                logger.info(f"Email sent successfully to {email}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise
            
        finally:
            # Clean up the file
            if os.path.exists(filename):
                os.remove(filename)
                logger.info(f"Cleaned up temporary file: {filename}")
    
    except Exception as e:
        logger.error(f"Error in generate_tax_report: {str(e)}")
        raise ValueError(f"Failed to generate and send tax report: {str(e)}")
