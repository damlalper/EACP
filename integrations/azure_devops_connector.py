"""
Azure DevOps connector for EACP
"""

from typing import Dict, Any
from integrations.base_connector import BaseConnector
import logging
try:
    import requests
except Exception:
    requests = None
import base64
import json

logger = logging.getLogger(__name__)


class AzureDevOpsConnector(BaseConnector):
    """Connector for Azure DevOps integration using REST API (PAT)

    Requires config keys: `organization`, `project`, `personal_access_token`.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.organization = config.get("organization", "")
        self.project = config.get("project", "")
        self.personal_access_token = config.get("personal_access_token", "")
        if requests:
            self.session = requests.Session()
        else:
            self.session = None

    def _auth_header(self) -> Dict[str, str]:
        token = f":{self.personal_access_token}".encode()
        basic = base64.b64encode(token).decode()
        return {"Authorization": f"Basic {basic}"}

    def authenticate(self) -> bool:
        """Validate PAT by calling a simple Azure DevOps API (projects list)."""
        if not self.session:
            logger.warning("'requests' not available; skipping Azure DevOps auth (running in mock mode)")
            self.authenticated = False
            return False

        try:
            headers = {"Content-Type": "application/json"}
            headers.update(self._auth_header())
            url = f"https://dev.azure.com/{self.organization}/_apis/projects?api-version=6.0"
            resp = self.session.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                self.authenticated = True
                return True
            logger.error(f"Azure DevOps auth failed: {resp.status_code} {resp.text}")
            return False
        except Exception as e:
            logger.error(f"Azure DevOps authentication error: {str(e)}")
            return False

    def test_connection(self) -> bool:
        if not self.authenticated:
            return self.authenticate()
        return True

    def create_work_item(self, title: str, description: str,
                         work_item_type: str = "Task", **kwargs) -> Dict[str, Any]:
        """Create a work item via Azure DevOps REST API.

        Example: work_item_type = "Task", "Bug", "User Story" etc.
        """
        if not self.authenticated:
            if not self.authenticate():
                # if requests not available, fall back to local mock response
                if not self.session:
                    logger.warning("Falling back to local mock Azure DevOps response")
                    return {
                        "id": hash(title) % 100000,
                        "title": title,
                        "description": description,
                        "type": work_item_type,
                        "state": "New",
                        "project": self.project,
                        **kwargs,
                    }
                raise RuntimeError("Azure DevOps authentication failed")

        try:
            url = (
                f"https://dev.azure.com/{self.organization}/{self.project}/_apis/wit/workitems/${work_item_type}?api-version=6.0"
            )
            headers = {"Content-Type": "application/json-patch+json"}
            headers.update(self._auth_header())
            patch = [
                {"op": "add", "path": "/fields/System.Title", "value": title},
                {"op": "add", "path": "/fields/System.Description", "value": description},
            ]
            # include additional fields from kwargs
            for k, v in kwargs.items():
                patch.append({"op": "add", "path": f"/fields/{k}", "value": v})

            resp = self.session.post(url, headers=headers, data=json.dumps(patch), timeout=10)
            if resp.status_code in (200, 201):
                return resp.json()
            logger.error(f"Failed to create work item: {resp.status_code} {resp.text}")
            raise RuntimeError(f"Azure DevOps create_work_item error: {resp.status_code}")
        except Exception as e:
            logger.error(f"Failed to create Azure DevOps work item: {str(e)}")
            raise
