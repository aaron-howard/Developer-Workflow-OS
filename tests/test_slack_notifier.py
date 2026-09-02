import json
from unittest.mock import patch, MagicMock
from app.server.slack_notifier import SlackNotifier

def test_slack_notifier_success():
    notifier = SlackNotifier("https://fake-webhook.url")
    payload = {
        "status": "ready",
        "result": {"score": 95}
    }
    
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        success = notifier.post_routine_result("release_readiness", payload)
        
        assert success is True
        mock_urlopen.assert_called_once()
        
        # Verify the payload format
        req = mock_urlopen.call_args[0][0]
        sent_data = json.loads(req.data.decode('utf-8'))
        
        assert "blocks" in sent_data
        assert sent_data["blocks"][0]["text"]["text"] == "Agentic OS: Release Readiness"
        assert sent_data["blocks"][1]["text"]["text"] == "*release_readiness* completed with status ✅ `ready` (Score: 95)"

def test_slack_notifier_no_url():
    notifier = SlackNotifier("")
    success = notifier.post_routine_result("test", {})
    assert success is False
