import pandas as pd
import os
from morshed_squad.database.database_manager import DatabaseManager

class ExcelManager:
    """
    Handles importing leads from Excel/CSV and exporting outreach reports.
    """
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def import_leads(self, file_path):
        """Reads Excel/CSV and adds to DB."""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Expected columns: Name, Phone, Email (Email optional)
            count = 0
            for _, row in df.iterrows():
                name = str(row.get('Name', '')).strip()
                phone = str(row.get('Phone', '')).strip()
                email = str(row.get('Email', '')).strip() if 'Email' in row else None
                
                if name and phone:
                    res = self.db.add_lead(name, phone, email)
                    if res:
                        count += 1
            return f"Successfully imported {count} leads."
        except Exception as e:
            return f"Import failed: {str(e)}"

    def export_report(self, output_path="outreach_report.xlsx"):
        """Generates an Excel report of all leads and logs."""
        try:
            leads = self.db.get_all_leads()
            logs = self.db.get_telephony_logs()
            
            df_leads = pd.DataFrame(leads)
            df_logs = pd.DataFrame(logs)
            
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df_leads.to_excel(writer, sheet_name='Leads', index=False)
                df_logs.to_excel(writer, sheet_name='Telephony Logs', index=False)
            
            return f"Report exported to {output_path}"
        except Exception as e:
            return f"Export failed: {str(e)}"
