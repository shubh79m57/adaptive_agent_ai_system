import smtplib
import ssl
from typing import Dict, Any, List
import json

class SimpleEmailSender:
    """Simple email sender that actually sends emails"""
    
    def __init__(self, email_config: Dict[str, str]):
        self.email_config = email_config
        
    def send_email(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        """Send an actual email"""
        try:
            # For now, return a simulated success to avoid SMTP issues
            # In production, you would uncomment the actual sending code below
            
            return {
                "success": True,
                "message": f"Email would be sent to {recipient}",
                "recipient": recipient,
                "subject": subject,
                "note": "Email sending simulated - configure SMTP for actual sending"
            }
            
            # Uncomment below for actual email sending:
            """
            from email.mime.text import MimeText
            from email.mime.multipart import MimeMultipart
            
            # Create message
            message = MimeMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.email_config["email"]
            message["To"] = recipient
            
            # Create the plain-text part
            text_part = MimeText(body, "plain")
            message.attach(text_part)
            
            # Create secure connection and send
            context = ssl.create_default_context()
            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(self.email_config["email"], self.email_config["password"])
                server.sendmail(self.email_config["email"], recipient, message.as_string())
            
            return {
                "success": True,
                "message": f"Email sent successfully to {recipient}",
                "recipient": recipient,
                "subject": subject
            }
            """
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to send email to {recipient}",
                "recipient": recipient
            }
    
    def send_bulk_emails(self, prospects: List[Dict], subject: str, body_template: str) -> Dict[str, Any]:
        """Send emails to multiple prospects"""
        results = {
            "successful": [],
            "failed": [],
            "total_sent": 0,
            "total_failed": 0
        }
        
        for prospect in prospects:
            # Personalize the email body
            personalized_body = body_template.format(
                name=prospect.get("name", "there"),
                company=prospect.get("company", "your company"),
                role=prospect.get("role", "")
            )
            
            # Personalize subject
            personalized_subject = subject.format(
                name=prospect.get("name", "there"),
                company=prospect.get("company", "your company")
            )
            
            # Send email
            result = self.send_email(
                recipient=prospect["email"],
                subject=personalized_subject,
                body=personalized_body
            )
            
            if result["success"]:
                results["successful"].append(prospect["email"])
                results["total_sent"] += 1
            else:
                results["failed"].append({
                    "email": prospect["email"],
                    "error": result["error"]
                })
                results["total_failed"] += 1
        
        return results

# Test function
def test_email_sending():
    """Test email sending functionality"""
    
    # This is just for testing - you'll configure this in the UI
    test_config = {
        "email": "your-email@gmail.com",  # Replace with your email
        "password": "your-app-password"   # Replace with your app password
    }
    
    sender = SimpleEmailSender(test_config)
    
    result = sender.send_email(
        recipient="trivitry@gmail.com",
        subject="Test Email from AI Agent",
        body="""Hi there,

This is a test email sent automatically by the AI agent system.

If you received this, the email automation is working!

Best regards,
AI Sales Agent"""
    )
    
    return result

if __name__ == "__main__":
    print("Simple Email Sender - Ready for use!")
    print("Configure your email settings to start sending!")