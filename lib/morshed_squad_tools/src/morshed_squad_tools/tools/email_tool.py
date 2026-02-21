import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
from pydantic import Field, BaseModel
from typing import Type
from crewai.tools import BaseTool

class EmailSchema(BaseModel):
    """Input for EmailTool."""
    recipient_email: str = Field(..., description="The email address to send the report to.")
    subject: str = Field(..., description="The subject line of the email.")
    body: str = Field(..., description="The main content or report to send in the email body.")

class MorshedEmailTool(BaseTool):
    name: str = "Email Tool"
    description: str = "A tool to send an email report to a specific address. Use this only when you are completely finished with your research and ready to deliver the final product."
    args_schema: Type[BaseModel] = EmailSchema
    
    # Store credentials at instance level so agents don't see them
    sender_email: str = Field(default="")
    sender_password: str = Field(default="")
    user_id: int = Field(default=1)

    def _run(self, recipient_email: str, subject: str, body: str) -> str:
        """Send an email using SMTP."""
        import time
        from morshed_squad.database.database_manager import DatabaseManager
        
        db = DatabaseManager(user_id=self.user_id)
        
        # 1. Queue action for Human Approval
        details = f"To: {recipient_email}\nSubject: {subject}\n\n{body}"
        action_id = db.create_pending_action('Email Dispatch', details)
        
        if not action_id:
            return "Error queuing the action for approval."
            
        # 2. Block until Approved or Rejected
        loading_time = 0
        while True:
            status, feedback = db.check_action_status(action_id)
            if status == 'Approved':
                break
            elif status == 'Rejected':
                return f"ACTION REJECTED BY HUMAN. Feedback: {feedback or 'None'}. You MUST revise your approach based on this feedback."
            time.sleep(3)
            loading_time += 3
            if loading_time > 600: # 10 minute timeout
                return "Error: Human took too long to respond. Task timed out."
                
        # 3. Execute the approved action
        load_dotenv() # Load from .env if present
        
        # Fallback to .env if UI didn't provide credentials
        active_email = self.sender_email or os.environ.get("AGENT_GMAIL_ADDRESS")
        active_password = self.sender_password or os.environ.get("AGENT_GMAIL_APP_PASSWORD")

        if not active_email or not active_password:
            return "Error: Sender email credentials are not configured in Settings or .env file."
            
        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = subject
            msg['From'] = active_email
            msg['To'] = recipient_email

            # Connect to Gmail SMTP (Assuming Gmail for the user's config)
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(active_email, active_password)
            server.send_message(msg)
            server.quit()
            
            return f"Success: Email sent to {recipient_email}."
        except smtplib.SMTPAuthenticationError:
            return "Error: Authentication failed. Check the App Password in Settings."
        except Exception as e:
            return f"Error sending email: {str(e)}"
