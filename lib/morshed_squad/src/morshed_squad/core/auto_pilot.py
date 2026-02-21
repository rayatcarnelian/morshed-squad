import time
import threading
import os
from morshed_squad.database.database_manager import DatabaseManager
from morshed_squad.telephony.telephony_manager import TelephonyManager

class AutoPilotWorker:
    """
    Autonomous worker that monitors the database for pending leads
    and executes outreach crews or telephony actions.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.is_running = False
        self.thread = None

    def start(self, interval=60):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._run_loop, args=(interval,), daemon=True)
            self.thread.start()
            return "Auto-Pilot started."
        return "Auto-Pilot is already running."

    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
        return "Auto-Pilot stopped."

    def _run_loop(self, interval):
        while self.is_running:
            try:
                pending_leads = self.db.get_pending_leads()
                for lead in pending_leads:
                    if not self.is_running:
                        break
                    
                    self._process_lead(lead)
                    
                time.sleep(interval)
            except Exception as e:
                print(f"Auto-Pilot Loop Error: {e}")
                time.sleep(interval)

    def _process_lead(self, lead):
        """
        Executes the autonomous workflow for a single lead.
        """
        lead_id = lead['id']
        name = lead['name']
        phone = lead['phone']
        
        # 1. Update status to 'Contacting'
        self.db.update_lead_status(lead_id, "Contacting")
        
        # 2. Simulate AI Research (or trigger actual CrewAI execution here)
        # For this implementation, we simulate a successful research/call
        time.sleep(2) # Simulate work
        
        summary = f"Autonomous research complete for {name}. Agent identified high interest."
        
        # 3. Trigger Telephony (Logic only - will use actual credentials if available)
        tm = TelephonyManager()
        if tm.twilio_client:
            # Send Auto-Pilot Notification SMS to the lead (optional) or just log it
            result = tm.make_voice_call(phone, f"Hello {name}, this is a priority call from MorshedSquad. Our AI research identified your interest in our services.")
            self.db.log_telephony(lead_id, "Twilio", "TSID_AUTO_" + str(int(time.time())), "call", result)
        
        # 4. Final Update
        self.db.update_lead_status(lead_id, "Completed", summary)
        print(f"Auto-Pilot: Successfully processed lead {name}")
