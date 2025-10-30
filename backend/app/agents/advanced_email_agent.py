import smtplib
import imaplib
import email as email_module
import time
import csv
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
import re

class AdvancedEmailAgent:
    """
    Advanced Email Agent that can:
    - Send bulk emails to prospect lists
    - Monitor inbox for replies
    - Intelligently categorize responses
    - Generate automated replies
    - Maintain email threads
    """
    
    def __init__(self, email_config: Dict[str, str]):
        self.email_config = email_config
        self.conversation_threads = {}  # Store email threads
        self.prospect_status = {}  # Track prospect status
        
    def load_prospect_list(self, csv_file_path: str) -> List[Dict]:
        """Load prospects from CSV file"""
        prospects = []
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    prospects.append({
                        'email': row.get('email', ''),
                        'name': row.get('name', ''),
                        'company': row.get('company', ''),
                        'role': row.get('role', ''),
                        'context': row.get('context', 'general outreach')
                    })
        except Exception as e:
            print(f"Error loading prospect list: {e}")
        return prospects
    
    def generate_personalized_email(self, prospect: Dict) -> Dict[str, str]:
        """Generate personalized email for each prospect"""
        
        # Email templates based on role
        templates = {
            'ceo': {
                'subject': f"Strategic growth opportunity for {prospect['company']}",
                'body': f"""Hi {prospect['name']},

I've been following {prospect['company']}'s growth and I'm impressed by your recent achievements.

Many CEOs in your industry are facing challenges with operational efficiency and scaling their teams. We've helped companies like yours achieve:
• 40% increase in team productivity
• 60% reduction in manual processes
• 25% faster time-to-market

Worth a 15-minute conversation to explore how this could apply to {prospect['company']}?

Best regards,
[Your Name]
[Your Title]
[Your Company]"""
            },
            'vp': {
                'subject': f"Helping VPs like you exceed targets - {prospect['company']}",
                'body': f"""Hi {prospect['name']},

As a VP at {prospect['company']}, you're likely focused on hitting ambitious targets while optimizing team performance.

We've helped VPs in similar roles achieve:
• 35% improvement in team efficiency
• 50% reduction in administrative overhead
• 20% increase in deal velocity

Interested in a brief call to discuss how this could work for your team?

Best,
[Your Name]"""
            },
            'default': {
                'subject': f"Quick question about {prospect['company']}",
                'body': f"""Hi {prospect['name']},

I came across {prospect['company']} and was impressed by your work in the industry.

We've been helping companies like yours streamline operations and drive better results. Our clients typically see:
• Improved operational efficiency
• Better team productivity
• Faster decision-making processes

Worth a brief conversation to see if there's a fit?

Best regards,
[Your Name]"""
            }
        }
        
        # Select template based on role
        role_key = 'default'
        for key in templates.keys():
            if key in prospect['role'].lower():
                role_key = key
                break
                
        template = templates[role_key]
        
        return {
            'subject': template['subject'],
            'body': template['body'],
            'recipient': prospect['email']
        }
    
    def send_bulk_emails(self, prospects: List[Dict], delay_seconds: int = 30):
        """Send personalized emails to list of prospects"""
        
        print(f"Starting bulk email campaign to {len(prospects)} prospects...")
        
        # Email server configuration (example for Gmail)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        try:
            # Connect to SMTP server
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(self.email_config['email'], self.email_config['password'])
            
            successful_sends = 0
            failed_sends = 0
            
            for prospect in prospects:
                try:
                    # Generate personalized email
                    email_content = self.generate_personalized_email(prospect)
                    
                    # Create email message
                    msg = MimeMultipart()
                    msg['From'] = self.email_config['email']
                    msg['To'] = prospect['email']
                    msg['Subject'] = email_content['subject']
                    
                    # Add body
                    body = email_content['body']
                    msg.attach(MimeText(body, 'plain'))
                    
                    # Send email
                    text = msg.as_string()
                    server.sendmail(self.email_config['email'], prospect['email'], text)
                    
                    # Track sent email
                    self.prospect_status[prospect['email']] = {
                        'status': 'sent',
                        'sent_at': datetime.now().isoformat(),
                        'subject': email_content['subject'],
                        'prospect_info': prospect
                    }
                    
                    successful_sends += 1
                    print(f"✅ Email sent to {prospect['name']} ({prospect['email']})")
                    
                    # Delay between emails to avoid being flagged as spam
                    time.sleep(delay_seconds)
                    
                except Exception as e:
                    failed_sends += 1
                    print(f"❌ Failed to send to {prospect['email']}: {e}")
            
            server.quit()
            
            print(f"\n📊 Campaign Summary:")
            print(f"✅ Successful sends: {successful_sends}")
            print(f"❌ Failed sends: {failed_sends}")
            print(f"📧 Total emails processed: {len(prospects)}")
            
        except Exception as e:
            print(f"SMTP connection error: {e}")
    
    def monitor_inbox_for_replies(self):
        """Monitor inbox for replies and process them"""
        
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(self.email_config['email'], self.email_config['password'])
            mail.select('inbox')
            
            # Search for recent emails
            date_since = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")
            _, message_numbers = mail.search(None, f'SINCE {date_since}')
            
            for num in message_numbers[0].split():
                _, msg_data = mail.fetch(num, '(RFC822)')
                email_msg = email_module.message_from_bytes(msg_data[0][1])
                
                # Extract email details
                sender = email_msg['From']
                subject = email_msg['Subject']
                
                # Check if this is a reply to our outreach
                if self.is_reply_to_outreach(sender, subject):
                    body = self.extract_email_body(email_msg)
                    response_analysis = self.analyze_response(body)
                    
                    print(f"\n📨 Reply received from {sender}")
                    print(f"Subject: {subject}")
                    print(f"Analysis: {response_analysis['category']}")
                    
                    # Handle the response
                    self.handle_response(sender, response_analysis, email_msg)
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            print(f"Error monitoring inbox: {e}")
    
    def is_reply_to_outreach(self, sender: str, subject: str) -> bool:
        """Check if email is a reply to our outreach"""
        # Extract email from sender string
        email_match = re.search(r'<(.+?)>', sender)
        sender_email = email_match.group(1) if email_match else sender
        
        # Check if we sent an email to this address
        return sender_email in self.prospect_status
    
    def extract_email_body(self, email_msg) -> str:
        """Extract plain text body from email"""
        if email_msg.is_multipart():
            for part in email_msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode('utf-8')
        else:
            return email_msg.get_payload(decode=True).decode('utf-8')
        return ""
    
    def analyze_response(self, email_body: str) -> Dict[str, Any]:
        """Analyze email response using rule-based intelligence"""
        
        body_lower = email_body.lower()
        
        # Interest indicators
        interest_keywords = ['interested', 'tell me more', 'schedule', 'call', 'meeting', 'demo', 'learn more', 'sounds good']
        not_interested_keywords = ['not interested', 'no thank you', 'remove', 'unsubscribe', 'stop', 'not looking']
        question_keywords = ['how', 'what', 'when', 'where', 'why', 'can you', 'could you', '?']
        timing_keywords = ['not right now', 'maybe later', 'next quarter', 'next year', 'busy', 'timing']
        
        # Calculate scores
        interest_score = sum(1 for keyword in interest_keywords if keyword in body_lower)
        not_interested_score = sum(1 for keyword in not_interested_keywords if keyword in body_lower)
        question_score = sum(1 for keyword in question_keywords if keyword in body_lower)
        timing_score = sum(1 for keyword in timing_keywords if keyword in body_lower)
        
        # Determine category
        if not_interested_score > 0:
            category = "not_interested"
            confidence = 0.9
        elif interest_score > 0:
            category = "interested" 
            confidence = 0.8
        elif question_score > 0:
            category = "has_questions"
            confidence = 0.7
        elif timing_score > 0:
            category = "bad_timing"
            confidence = 0.7
        else:
            category = "neutral"
            confidence = 0.5
        
        return {
            'category': category,
            'confidence': confidence,
            'interest_score': interest_score,
            'question_score': question_score,
            'body': email_body
        }
    
    def handle_response(self, sender: str, analysis: Dict, original_email):
        """Handle response based on analysis"""
        
        category = analysis['category']
        
        if category == "interested":
            self.send_meeting_scheduling_email(sender)
        elif category == "has_questions":
            self.send_question_response_email(sender, analysis['body'])
        elif category == "bad_timing":
            self.schedule_follow_up(sender, days=90)
        elif category == "not_interested":
            self.mark_as_unsubscribed(sender)
        
        # Update prospect status
        sender_email = re.search(r'<(.+?)>', sender).group(1) if '<' in sender else sender
        if sender_email in self.prospect_status:
            self.prospect_status[sender_email]['last_response'] = {
                'category': category,
                'received_at': datetime.now().isoformat(),
                'body': analysis['body']
            }
    
    def send_meeting_scheduling_email(self, recipient: str):
        """Send meeting scheduling email to interested prospects"""
        
        subject = "Let's schedule that conversation"
        body = """Thank you for your interest! 

I'd love to show you exactly how we can help your team achieve similar results.

I have availability for a 15-minute call:
• Tomorrow at 2:00 PM
• Thursday at 10:00 AM  
• Friday at 3:00 PM

Which works best for you? Or feel free to suggest another time.

Looking forward to our conversation!

Best regards,
[Your Name]"""
        
        self.send_single_email(recipient, subject, body)
        print(f"📅 Sent meeting scheduling email to {recipient}")
    
    def send_question_response_email(self, recipient: str, question_body: str):
        """Send response to prospect questions"""
        
        # Simple question analysis and response
        if "price" in question_body.lower() or "cost" in question_body.lower():
            response = """Great question about pricing!

Our solution is designed to provide ROI within 60 days. Most clients see cost savings that exceed the investment through improved efficiency alone.

I'd love to show you our ROI calculator in a brief call - it takes your specific numbers into account.

When would be a good time to discuss?"""
        
        elif "how" in question_body.lower():
            response = """Thanks for your question about implementation!

The process is typically:
1. Initial assessment (1 week)
2. Customization and setup (2-3 weeks)  
3. Team training (1 week)
4. Go-live support (ongoing)

Most clients are fully operational within 4-6 weeks.

Would you like to discuss the specifics for your situation?"""
        
        else:
            response = """Thanks for your reply and great question!

I'd love to give you a detailed answer that's specific to your situation. 

Would you be available for a brief 15-minute call this week? I can walk you through everything and answer any other questions you might have.

What's your availability like?"""
        
        subject = "Re: Your question about our solution"
        self.send_single_email(recipient, subject, response)
        print(f"❓ Sent question response email to {recipient}")
    
    def send_single_email(self, recipient: str, subject: str, body: str):
        """Send a single email"""
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.email_config['email'], self.email_config['password'])
            
            msg = MimeMultipart()
            msg['From'] = self.email_config['email']
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MimeText(body, 'plain'))
            
            server.sendmail(self.email_config['email'], recipient, msg.as_string())
            server.quit()
            
        except Exception as e:
            print(f"Error sending email to {recipient}: {e}")
    
    def schedule_follow_up(self, recipient: str, days: int):
        """Schedule follow-up for later"""
        follow_up_date = datetime.now() + timedelta(days=days)
        print(f"📅 Scheduled follow-up for {recipient} on {follow_up_date.date()}")
        
        # In a real system, you'd store this in a database or task queue
        
    def mark_as_unsubscribed(self, recipient: str):
        """Mark prospect as unsubscribed"""
        sender_email = re.search(r'<(.+?)>', recipient).group(1) if '<' in recipient else recipient
        if sender_email in self.prospect_status:
            self.prospect_status[sender_email]['unsubscribed'] = True
        print(f"🚫 Marked {sender_email} as unsubscribed")
    
    def get_campaign_stats(self) -> Dict[str, Any]:
        """Get campaign performance statistics"""
        
        total_sent = len(self.prospect_status)
        replied = sum(1 for prospect in self.prospect_status.values() if 'last_response' in prospect)
        interested = sum(1 for prospect in self.prospect_status.values() 
                        if 'last_response' in prospect and 
                        prospect['last_response']['category'] == 'interested')
        
        stats = {
            'total_sent': total_sent,
            'total_replies': replied,
            'interested_replies': interested,
            'response_rate': (replied / total_sent * 100) if total_sent > 0 else 0,
            'interest_rate': (interested / total_sent * 100) if total_sent > 0 else 0
        }
        
        return stats

# Example usage
def run_email_campaign():
    """Example of how to run a complete email campaign"""
    
    # Email configuration (you'd store this securely)
    email_config = {
        'email': 'your-email@gmail.com',
        'password': 'your-app-password'  # Use app password for Gmail
    }
    
    # Initialize the advanced email agent
    agent = AdvancedEmailAgent(email_config)
    
    # Load prospects from CSV
    prospects = agent.load_prospect_list('prospects.csv')
    
    # Send bulk emails
    agent.send_bulk_emails(prospects, delay_seconds=60)
    
    # Monitor for replies (run this periodically)
    agent.monitor_inbox_for_replies()
    
    # Get campaign statistics
    stats = agent.get_campaign_stats()
    print(f"\n📊 Campaign Statistics:")
    print(f"Response Rate: {stats['response_rate']:.1f}%")
    print(f"Interest Rate: {stats['interest_rate']:.1f}%")

if __name__ == "__main__":
    run_email_campaign()