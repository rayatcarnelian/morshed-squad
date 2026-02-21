from pydantic import Field, BaseModel
from typing import Type
from crewai.tools import BaseTool
from morshed_squad.database.database_manager import DatabaseManager

class SocialContentSchema(BaseModel):
    """Input for SocialContentTool."""
    platform: str = Field(..., description="The social media platform (e.g., Twitter, LinkedIn).")
    topic: str = Field(..., description="A short description of the topic being posted about.")
    content: str = Field(..., description="The exact generated text of the post, including hashtags and emojis.")

class MorshedSocialContentTool(BaseTool):
    name: str = "Social Content Drafter Tool"
    description: str = (
        "A tool to save a drafted social media post directly to the company's central database "
        "so the manager can review and approve it. ALWAYS use this tool once you are finished drafting a post."
    )
    args_schema: Type[BaseModel] = SocialContentSchema

    user_id: int = Field(default=1)

    def _run(self, platform: str, topic: str, content: str) -> str:
        """Save social post to local database."""
        import time
        from morshed_squad.database.database_manager import DatabaseManager
        
        try:
            db = DatabaseManager(user_id=self.user_id)
            
            # 1. Queue action for Human Approval
            details = f"Platform: {platform}\nTopic: {topic}\n\nContent:\n{content}"
            action_id = db.create_pending_action('Social Media Post', details)
            
            if not action_id:
                return "Error queuing the post for approval."
                
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
            
            # 3. If approved, officially log it in the standard social_posts table
            post_id = db.save_social_post(platform, topic, content)
            db.update_social_post(post_id, 'Approved', content)
            return f"Action Successful: Post drafted for {platform} on topic '{topic}' was APPROVED by the human."
        except Exception as e:
            return f"Error drafting post: {str(e)}"
