import os
import requests
import json
from twilio.rest import Client

class TelephonyManager:
    """
    Manages telephony operations across multiple providers (Twilio, Vapi).
    Designed for autonomous agent usage within the Morshed Squad platform.
    """
    def __init__(self, twilio_sid=None, twilio_token=None, twilio_from=None, vapi_key=None):
        self.twilio_sid = twilio_sid or os.getenv("TWILIO_SID")
        self.twilio_token = twilio_token or os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from = twilio_from or os.getenv("TWILIO_FROM_NUMBER")
        self.vapi_key = vapi_key or os.getenv("VAPI_API_KEY")
        
        self.twilio_client = None
        if self.twilio_sid and self.twilio_token:
            try:
                self.twilio_client = Client(self.twilio_sid, self.twilio_token)
            except Exception as e:
                print(f"Twilio Init Error: {e}")

    def send_sms(self, to_number, message):
        """Send an SMS via Twilio."""
        if not self.twilio_client:
            return "Error: Twilio not configured."
        try:
            msg = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_from,
                to=to_number
            )
            return f"SMS Sent. SID: {msg.sid}"
        except Exception as e:
            return f"SMS Failed: {str(e)}"

    def make_voice_call(self, to_number, text_to_say):
        """Initiate a standard voice call via Twilio with TwiML."""
        if not self.twilio_client:
            return "Error: Twilio not configured."
        try:
            twiml = f"<Response><Say voice='Polly.Joanna-Neural'>{text_to_say}</Say></Response>"
            call = self.twilio_client.calls.create(
                twiml=twiml,
                to=to_number,
                from_=self.twilio_from
            )
            return f"Call Initiated. SID: {call.sid}"
        except Exception as e:
            return f"Voice Call Failed: {str(e)}"

    def get_call_transcript(self, call_id):
        """
        Fetch transcript for a specific call.
        For Vapi, this would call the /call/:id endpoint.
        """
        if not self.vapi_key:
            return "Transcript unavailable (Vapi not configured). This call might be a standard Twilio voice call or manual outreach."
            
        url = f"https://api.vapi.ai/call/{call_id}"
        headers = {"Authorization": f"Bearer {self.vapi_key}"}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                transcript = data.get('transcript', 'Transcript is still processing or unavailable.')
                return transcript
            return f"Vapi Error {response.status_code}: Unable to fetch transcript."
        except Exception as e:
            # Fallback for demo/dev: return a mock transcript if it starts with 'VAPI_FAKE_'
            if str(call_id).startswith("VAPI_FAKE_"):
                return "Agent: Hello, this is Morshed Squad. How can I help you today?\nLead: I am interested in your AI automation services.\nAgent: Great! We can set up a meeting for tomorrow at 10 AM.\nLead: That works for me."
            return f"Transcript fetch failed: {str(e)}"

    def trigger_vapi_call(self, to_number, phone_id_or_assistant_id):
        """Trigger an AI voice assistant call via Vapi."""
        if not self.vapi_key:
            return "Error: Vapi API Key not configured."
        
        url = "https://api.vapi.ai/call/phone"
        headers = {
            "Authorization": f"Bearer {self.vapi_key}",
            "Content-Type": "application/json"
        }
        
        # Refined Payload: Use 'customer' for the recipient number
        # and 'phoneNumberId' if it looks like a Vapi Phone ID
        payload = {
            "maxDurationSeconds": 3600,
            "assistantId": phone_id_or_assistant_id if len(phone_id_or_assistant_id) > 20 else None, # Heuristic
            "phoneNumberId": phone_id_or_assistant_id if len(phone_id_or_assistant_id) <= 20 else None,
            "customer": {
                "number": to_number
            }
        }
        
        # If we have twilio credentials, we might need to pass them if using custom provider
        # But usually Vapi handles this via the Dashboard. 
        # For now, let's stick to a cleaner customer-centric payload.
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code in [200, 201]:
                return f"Vapi Call Started. ID: {response.json().get('id')}"
            else:
                # If it fails with the refined payload, try a fallback structure
                fallback_payload = {
                    "assistantId": phone_id_or_assistant_id,
                    "phoneNumber": {
                        "customerNumber": to_number
                    }
                }
                response = requests.post(url, headers=headers, json=fallback_payload)
                if response.status_code in [200, 201]:
                    return f"Vapi Call Started (Fallback). ID: {response.json().get('id')}"
                return f"Vapi Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Vapi Request Failed: {str(e)}"
