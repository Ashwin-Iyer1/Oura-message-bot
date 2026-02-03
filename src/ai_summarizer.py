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
        readiness_data: Dict[str, Any],
        stress_data: Dict[str, Any] = {},
        spo2_data: Dict[str, Any] = {},
        workout_data: Dict[str, Any] = {}
    ) -> str:
        """
        Generates a health summary using OpenAI based on Oura data.
        """
        
        # Prepare context for the LLM
        context = {
            "sleep": sleep_data.get("data", []),
            "activity": activity_data.get("data", []),
            "readiness": readiness_data.get("data", []),
            "stress": stress_data.get("data", []),
            "spo2": spo2_data.get("data", []),
            "workouts": workout_data.get("data", [])
        }
        
        # Limit data size if necessary by taking only the last item if list is long
        # But usually we call this with yesterday/today range so it should be small.
        
        prompt = f"""
        Analyze this Oura data. Output strictly HTML-formatted for Telegram (<b>, <i> only).
        
        Data:
        {json.dumps(context, indent=2)}
        
        Requirements:
        - <b>Stats</b>: Key metrics (Sleep, Readiness, Activity, HRV, RHR, Stress, SpO2) with values.
        - <b>Insights</b>: High-value correlations.
        - <b>Action</b>: 1 brief tip.
        
        Rules:
        - Absolute minimum words. Data-heavy.
        - No Markdown (** or __).
        - No HTML lists (<ul>, <li>) or <br>.
        - Use "• " for bullets.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful health assistant. Output ONLY HTML supported by Telegram (b, i). NO ul/li tags."},
                    {"role": "user", "content": prompt}
                ],
            )
            content = response.choices[0].message.content.strip()
            # Failsafe: Remove any Markdown bold syntax if the LLM ignores instructions
            return content.replace("**", "").replace("__", "")
        except Exception as e:
            return f"Error generating summary: {e}"
