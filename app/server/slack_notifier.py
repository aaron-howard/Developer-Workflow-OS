import json
import urllib.request
import urllib.error
from typing import Any, Dict

class SlackNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def post_routine_result(self, routine_name: str, payload: Dict[str, Any]) -> bool:
        """Format the routine result and post it to Slack."""
        if not self.webhook_url:
            return False
            
        if not self.webhook_url.startswith("https://"):
            return False

        status = payload.get("status", "unknown")
        emoji = "✅" if status == "ok" or status == "ready" else "⚠️" if status == "watch" else "❌"
        
        result_content = payload.get("result", {})
        
        # Build text based on whether it's a release readiness check or generic digest
        if isinstance(result_content, dict) and "score" in result_content:
            text = f"*{routine_name}* completed with status {emoji} `{status}` (Score: {result_content.get('score')})"
        else:
            text = f"*{routine_name}* completed with status {emoji} `{status}`"
            
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Agentic OS: {routine_name.replace('_', ' ').title()}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text
                }
            }
        ]
        
        slack_payload = {"blocks": blocks}

        try:
            req = urllib.request.Request(
                self.webhook_url, 
                data=json.dumps(slack_payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status == 200
        except (urllib.error.URLError, ValueError, TimeoutError):
            return False
