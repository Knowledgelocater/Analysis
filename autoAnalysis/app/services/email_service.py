# app/services/email_service.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional
from ..config import settings


class EmailService:
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.sender_email = settings.SENDER_EMAIL
        self.sender_password = settings.SENDER_PASSWORD
    
    def send_dashboard_email(
        self, 
        recipient_email: str, 
        file_name: str,
        dashboard_path: str,
        analysis_path: Optional[str] = None
    ) -> bool:
        """
        Send dashboard HTML and analysis JSON to user via email.
        
        Args:
            recipient_email: User's email address
            file_name: Original uploaded file name
            dashboard_path: Path to generated dashboard HTML
            analysis_path: Optional path to analysis JSON
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.sender_email
            message["To"] = recipient_email
            message["Subject"] = f"📊 Data Analysis Report - {file_name}"
            
            # Email body
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; color: #333;">
                    <h2 style="color: #667eea;">📊 Data Analysis Report Ready!</h2>
                    
                    <p>Hello,</p>
                    
                    <p>Your data analysis for <strong>{file_name}</strong> has been completed successfully.</p>
                    
                    <p>This email contains:</p>
                    <ul>
                        <li><strong>Dashboard HTML</strong> - Interactive visualization of your data</li>
                        <li><strong>Analysis JSON</strong> - Detailed statistical report</li>
                    </ul>
                    
                    <h3>How to use:</h3>
                    <ol>
                        <li>Download the attached files</li>
                        <li>Open the <code>*_dashboard.html</code> file in your web browser</li>
                        <li>Explore the interactive dashboard with tabs for:
                            <ul>
                                <li>📈 Numeric Columns - Statistical summary</li>
                                <li>📋 Categorical Columns - Value distributions</li>
                                <li>🔗 Correlations - Relationships between variables</li>
                                <li>📝 Sample Data - First 5 rows</li>
                            </ul>
                        </li>
                    </ol>
                    
                    <p style="margin-top: 30px; color: #666; font-size: 12px;">
                        This is an automated email. Please do not reply to this message.
                    </p>
                </body>
            </html>
            """
            
            message.attach(MIMEText(body, "html"))
            
            # Attach dashboard HTML
            if os.path.exists(dashboard_path):
                self._attach_file(message, dashboard_path)
            
            # Attach analysis JSON if provided
            if analysis_path and os.path.exists(analysis_path):
                self._attach_file(message, analysis_path)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            print(f"✅ Email sent successfully to {recipient_email}")
            return True
        
        except Exception as e:
            print(f"❌ Failed to send email to {recipient_email}: {str(e)}")
            return False
    
    @staticmethod
    def _attach_file(message, file_path: str):
        """Attach a file to the email message."""
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(file_path)}"
            )
            message.attach(part)
        except Exception as e:
            print(f"Warning: Could not attach file {file_path}: {str(e)}")


# Create a singleton instance
email_service = EmailService()
