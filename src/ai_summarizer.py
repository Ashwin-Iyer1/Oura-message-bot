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
        
        Output Requirements:
        - <b>Statistics</b>: List key metrics (Sleep Score, Readiness, Activity, HRV, RHR) with values.
        - <b>Insights</b>: 1-2 bullet points correlating the data.
        - <b>Recommendations</b>: 1-2 brief, actionable tips for today.

        Style:
        - USE ONLY HTML TAGS (<b>, <i>).
        - DO NOT use Markdown syntax like **test** or __test__.
        - DO NOT use HTML list tags (<ul>, <li>). Telegram does not support them.
        - DO NOT use <br> tags. Use newlines for line breaks.
        - Use strict bullet points: "• " (e.g., "• High HRV...").
        - Check your output: if you see **, remove it.
        - Extremely concise. No fluff.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful health assistant. Output ONLY HTML supported by Telegram (b, i). NO ul/li tags."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            content = response.choices[0].message.content.strip()
            # Failsafe: Remove any Markdown bold syntax if the LLM ignores instructions
            return content.replace("**", "").replace("__", "")
        except Exception as e:
            return f"Error generating summary: {e}"
