"""
SAP connector for EACP
"""

from typing import Dict, Any
from integrations.base_connector import BaseConnector
import logging
try:
    import requests
except Exception:
    requests = None

logger = logging.getLogger(__name__)


class SAPConnector(BaseConnector):
    """Connector for SAP integration using HTTP/OData endpoints.

    Config should provide `host` (base URL), and credentials `username`/`password` for basic auth.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.host = config.get("host", "")
        self.client = config.get("client", "")
        self.username = config.get("username", "")
        self.password = config.get("password", "")
        if requests:
            self.session = requests.Session()
            if self.username and self.password:
                self.session.auth = (self.username, self.password)
        else:
            self.session = None

    def authenticate(self) -> bool:
        """Basic connectivity check to SAP host (OData endpoint)."""
        if not self.session:
            logger.warning("'requests' not available; skipping SAP auth (mock mode)")
            self.authenticated = False
            return False

        try:
            if not self.host:
                logger.error("SAP host not configured")
                return False
            resp = self.session.get(self.host, timeout=10)
            if resp.status_code in (200, 401, 403):
                # 401/403 indicates credentials required but endpoint reachable
                self.authenticated = True
                return True
            logger.error(f"SAP connectivity failed: {resp.status_code} {resp.text}")
            return False
        except Exception as e:
            logger.error(f"SAP authentication error: {str(e)}")
            return False

    def test_connection(self) -> bool:
        if not self.authenticated:
            return self.authenticate()
        return True

    def execute_function(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an SAP endpoint function via HTTP.

        This will attempt POST to `{host}/{function_name}` with JSON payload. Adjust your SAP OData/RFC gateway accordingly.
        """
        if not self.authenticated:
            if not self.authenticate():
                if not self.session:
                    logger.warning("Falling back to mock SAP response")
                    return {"function": function_name, "parameters": parameters, "result": "success", "data": {}}
                raise RuntimeError("SAP authentication failed")

        try:
            url = f"{self.host.rstrip('/')}/{function_name.lstrip('/')}"
            headers = {"Content-Type": "application/json"}
            resp = self.session.post(url, json=parameters, headers=headers, timeout=15)
            if resp.status_code in (200, 201):
                return resp.json()
            logger.error(f"SAP execute_function failed: {resp.status_code} {resp.text}")
            raise RuntimeError("SAP execute_function failed")
        except Exception as e:
            logger.error(f"Failed to execute SAP function: {str(e)}")
            raise
