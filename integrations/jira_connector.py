"""
JIRA connector for EACP
"""

from typing import Dict, Any, Optional
from integrations.base_connector import BaseConnector
import logging
try:
    import requests
except Exception:
    requests = None

logger = logging.getLogger(__name__)


class JiraConnector(BaseConnector):
    """Connector for JIRA integration using REST API.

    Config keys: `base_url` (e.g. https://your-domain.atlassian.net),
    `username` (email), `api_token` (Atlassian API token).
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "")
        self.username = config.get("username", "")
        self.api_token = config.get("api_token", "")
        if requests:
            self.session = requests.Session()
            if self.username and self.api_token:
                self.session.auth = (self.username, self.api_token)
        else:
            self.session = None

    def authenticate(self) -> bool:
        """Validate credentials by calling the JIRA myself endpoint."""
        if not self.session:
            logger.warning("'requests' not available; skipping JIRA auth (mock mode)")
            self.authenticated = False
            return False

        try:
            url = f"{self.base_url}/rest/api/3/myself"
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                self.authenticated = True
                return True
            logger.error(f"JIRA auth failed: {resp.status_code} {resp.text}")
            return False
        except Exception as e:
            logger.error(f"JIRA authentication error: {str(e)}")
            return False

    def test_connection(self) -> bool:
        if not self.authenticated:
            return self.authenticate()
        return True

    def create_ticket(self, title: str, description: str,
                     project_key: str = "PROJ", **kwargs) -> Dict[str, Any]:
        """Create a JIRA ticket via REST API."""
        if not self.authenticated:
            if not self.authenticate():
                if not self.session:
                    logger.warning("Falling back to mock JIRA ticket creation")
                    ticket = {"id": f"{project_key}-{hash(title) % 10000}", "key": f"{project_key}-{hash(title) % 10000}", "summary": title, "description": description}
                    return ticket
                raise RuntimeError("JIRA authentication failed")

        try:
            url = f"{self.base_url}/rest/api/3/issue"
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": title,
                    "description": description,
                    "issuetype": {"name": kwargs.get("issuetype", "Task")},
                }
            }
            # merge extra fields
            extra_fields = kwargs.get("fields", {})
            payload["fields"].update(extra_fields)

            headers = {"Content-Type": "application/json"}
            if not self.session:
                logger.warning("'requests' not available; returning mock JIRA ticket")
                return {"id": f"{project_key}-{hash(title) % 10000}", "key": f"{project_key}-{hash(title) % 10000}", "summary": title, "description": description}

            resp = self.session.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code in (200, 201):
                return resp.json()
            logger.error(f"Failed to create JIRA ticket: {resp.status_code} {resp.text}")
            raise RuntimeError("JIRA create_ticket failed")
        except Exception as e:
            logger.error(f"Failed to create JIRA ticket: {str(e)}")
            raise

    def assign_task(self, task_id: str, assignee: str, **kwargs) -> Dict[str, Any]:
        """Assign a JIRA task to a user (assignee expects accountId)."""
        if not self.authenticated:
            if not self.authenticate():
                if not self.session:
                    logger.warning("Falling back to mock assign_task")
                    return {"task_id": task_id, "assignee": assignee, "status": "assigned"}
                raise RuntimeError("JIRA authentication failed")

        try:
            url = f"{self.base_url}/rest/api/3/issue/{task_id}/assignee"
            payload = {"accountId": assignee}
            headers = {"Content-Type": "application/json"}
            if not self.session:
                logger.warning("'requests' not available; mock assign_task succeeded")
                return {"task_id": task_id, "assignee": assignee, "status": "assigned"}

            resp = self.session.put(url, json=payload, headers=headers, timeout=10)
            if resp.status_code in (200, 204):
                return {"task_id": task_id, "assignee": assignee, "status": "assigned"}
            logger.error(f"Failed to assign JIRA task: {resp.status_code} {resp.text}")
            raise RuntimeError("JIRA assign_task failed")
        except Exception as e:
            logger.error(f"Failed to assign JIRA task: {str(e)}")
            raise

    def update_status(self, task_id: str, status: str, **kwargs) -> Dict[str, Any]:
        """Transition an issue to a new status using transitions API."""
        if not self.authenticated:
            if not self.authenticate():
                raise RuntimeError("JIRA authentication failed")

        try:
            # need to find appropriate transition id for the desired status
            transitions_url = f"{self.base_url}/rest/api/3/issue/{task_id}/transitions"
            resp = self.session.get(transitions_url, timeout=10)
            if resp.status_code != 200:
                logger.error(f"Failed to fetch transitions: {resp.status_code} {resp.text}")
                raise RuntimeError("Failed to fetch transitions")

            transitions = resp.json().get("transitions", [])
            transition_id = None
            for t in transitions:
                if t.get("name", "").lower() == status.lower():
                    transition_id = t.get("id")
                    break

            if not transition_id:
                raise RuntimeError(f"Transition for status '{status}' not found")

            payload = {"transition": {"id": transition_id}}
            headers = {"Content-Type": "application/json"}
            resp2 = self.session.post(transitions_url, json=payload, headers=headers, timeout=10)
            if resp2.status_code in (200, 204):
                return {"task_id": task_id, "status": status, "updated": True}
            logger.error(f"Failed to update status: {resp2.status_code} {resp2.text}")
            raise RuntimeError("JIRA update_status failed")
        except Exception as e:
            logger.error(f"Failed to update JIRA task status: {str(e)}")
            raise
