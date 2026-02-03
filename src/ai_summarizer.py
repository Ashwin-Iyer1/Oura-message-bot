from openai import OpenAI
import json
from typing import Dict, Any

class AISummarizer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_health_summary(
        self, 
        sleep_data: Dict[str, Any], 
        activity_data: Dict[str, Any], 
        readiness_data: Dict[str, Any]
    ) -> str:
        """
        Generates a health summary using OpenAI based on Oura data.
        """
        
        # Prepare context for the LLM
        context = {
            "sleep": sleep_data.get("data", []),
            "activity": activity_data.get("data", []),
            "readiness": readiness_data.get("data", [])
        }
        
        # Limit data size if necessary by taking only the last item if list is long
        # But usually we call this with yesterday/today range so it should be small.
        
        prompt = f"""
        You are an expert personal health coach. Analyze the following Oura Ring data for the user.
        
        Data:
        {json.dumps(context, indent=2)}
        
        Please provide a concise, encouraging, and actionable daily summary. 
        - Highlight what went well.
        - Point out areas for improvement.
        - Give one specific tip for today based on this data.
        - Use emojis to make it friendly.
        - Keep it under 200 words.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful health assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating summary: {e}"
