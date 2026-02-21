from morshed_squad.tools.base_tool import BaseTool
from typing import Type, Optional
from pydantic import BaseModel, Field
from morshed_squad.telephony.telephony_manager import TelephonyManager

class TelephonyInput(BaseModel):
    """Input schema for TelephonyTool."""
    to_number: str = Field(..., description="The phone number to contact in E.164 format (e.g., +1234567890)")
    content: str = Field(..., description="The message to send via SMS or the text to say during a call.")
    action: str = Field(..., description="The action to perform: 'sms' or 'call'")

class MorshedTelephonyTool(BaseTool):
    name: str = "telephony_tool"
    description: str = (
        "A tool for sending SMS messages or making automated voice calls. "
        "Use 'action'='sms' to send a text message, or 'action'='call' to make a voice call where the 'content' will be spoken to the recipient."
    )
    args_schema: Type[BaseModel] = TelephonyInput

    def _run(self, to_number: str, content: str, action: str) -> str:
        manager = TelephonyManager()
        
        if action == "sms":
            return manager.send_sms(to_number, content)
        elif action == "call":
            return manager.make_voice_call(to_number, content)
        else:
            return f"Error: Invalid action '{action}'. Use 'sms' or 'call'."
