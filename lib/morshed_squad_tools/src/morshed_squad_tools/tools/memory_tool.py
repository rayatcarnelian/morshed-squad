from pydantic import Field, BaseModel
from typing import Type
from crewai.tools import BaseTool
from morshed_squad.database.database_manager import DatabaseManager

class MemoryStoreSchema(BaseModel):
    """Input for storing a memory."""
    memory_key: str = Field(..., description="A short, descriptive key for this memory (e.g., 'client_preference_tone', 'last_campaign_result').")
    memory_value: str = Field(..., description="The actual information to remember for future sessions.")

class MemoryRecallSchema(BaseModel):
    """Input for recalling a memory."""
    memory_key: str = Field(..., description="The key of the memory to recall.")

class MorshedMemoryStoreTool(BaseTool):
    name: str = "Memory Store Tool"
    description: str = (
        "Use this tool to permanently save important information to your long-term memory vault. "
        "This information will persist across completely separate crew executions and sessions. "
        "Use this to remember client preferences, past mistakes, key decisions, or any context "
        "that would be valuable in the future. Example keys: 'client_tone_preference', 'last_error_cause'."
    )
    args_schema: Type[BaseModel] = MemoryStoreSchema
    user_id: int = Field(default=1)

    def _run(self, memory_key: str, memory_value: str) -> str:
        try:
            db = DatabaseManager(user_id=self.user_id)
            db.save_agent_memory(memory_key, memory_value)
            return f"Memory successfully stored: '{memory_key}' = '{memory_value[:100]}...'"
        except Exception as e:
            return f"Error storing memory: {str(e)}"

class MorshedMemoryRecallTool(BaseTool):
    name: str = "Memory Recall Tool"
    description: str = (
        "Use this tool to recall information from your long-term memory vault. "
        "Provide the key of the memory you want to retrieve. If you are unsure of the exact key, "
        "use the key 'ALL' to retrieve every memory stored for this user."
    )
    args_schema: Type[BaseModel] = MemoryRecallSchema
    user_id: int = Field(default=1)

    def _run(self, memory_key: str) -> str:
        try:
            db = DatabaseManager(user_id=self.user_id)
            
            if memory_key.upper() == 'ALL':
                # Retrieve all memories for this user
                with db._get_connection() as conn:
                    import sqlite3
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT key, value, updated_at FROM agent_memory WHERE user_id = ? ORDER BY updated_at DESC",
                        (db.user_id,)
                    )
                    rows = [dict(r) for r in cursor.fetchall()]
                
                if not rows:
                    return "No memories found in your vault. Your long-term memory is empty."
                
                result = "=== LONG-TERM MEMORY VAULT ===\n"
                for r in rows:
                    result += f"[{r['key']}] = {r['value']} (saved: {r['updated_at']})\n---\n"
                return result
            else:
                with db._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT value FROM agent_memory WHERE user_id = ? AND key = ?",
                        (db.user_id, memory_key)
                    )
                    row = cursor.fetchone()
                
                if row:
                    return f"Memory recalled: '{memory_key}' = '{row[0]}'"
                else:
                    return f"No memory found for key '{memory_key}'. It may not have been stored yet."
        except Exception as e:
            return f"Error recalling memory: {str(e)}"
