"""
CRM connector for EACP (generic CRM interface)
"""

from typing import Dict, Any, Optional
from integrations.base_connector import BaseConnector
import logging
try:
    import requests
except Exception:
    requests = None

logger = logging.getLogger(__name__)


class CRMConnector(BaseConnector):
    """Generic CRM connector with HubSpot support.

    For HubSpot use `crm_type: hubspot` and provide `api_key` (private app access token).
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.crm_type = config.get("crm_type", "generic")  # salesforce, hubspot, etc.
        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "")
        if requests:
            self.session = requests.Session()
            if self.api_key:
                # HubSpot and many modern CRMs use Bearer tokens
                self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        else:
            self.session = None

    def authenticate(self) -> bool:
        """Basic validation of provided credentials depending on CRM type."""
        try:
            if self.crm_type.lower() == "hubspot":
                if not self.session:
                    logger.warning("'requests' not available; skipping HubSpot auth (mock mode)")
                    self.authenticated = False
                    return False
                url = "https://api.hubapi.com/oauth/v1/access-tokens"
                test_url = "https://api.hubapi.com/crm/v3/objects/contacts?limit=1"
                resp = self.session.get(test_url, timeout=10)
                if resp.status_code in (200, 204):
                    self.authenticated = True
                    return True
                logger.error(f"HubSpot auth failed: {resp.status_code} {resp.text}")
                return False

            # Fallback: assume provided credentials are acceptable
            self.authenticated = True
            return True
        except Exception as e:
            logger.error(f"CRM authentication error: {str(e)}")
            return False

    def test_connection(self) -> bool:
        if not self.authenticated:
            return self.authenticate()
        return True

    def create_contact(self, name: str, email: str, **kwargs) -> Dict[str, Any]:
        """Create a contact in CRM. Supports HubSpot if configured."""
        if not self.authenticated:
            if not self.authenticate():
                raise RuntimeError("CRM authentication failed")

        try:

            if self.crm_type.lower() == "hubspot":
                if not self.session:
                    logger.warning("'requests' not available; returning mock HubSpot contact")
                    return {"id": f"contact_{hash(email) % 100000}", "properties": {"email": email, "firstname": name}}
                url = "https://api.hubapi.com/crm/v3/objects/contacts"
                properties = {"email": email, "firstname": name}
                properties.update(kwargs.get("properties", {}))
                payload = {"properties": properties}
                headers = {"Content-Type": "application/json"}
                resp = self.session.post(url, json=payload, headers=headers, timeout=10)
                if resp.status_code in (200, 201):
                    return resp.json()
                logger.error(f"HubSpot create_contact failed: {resp.status_code} {resp.text}")
                raise RuntimeError("HubSpot create_contact failed")

            # Generic mock fallback (non-hubspot)
            contact = {"id": f"contact_{hash(email) % 100000}", "name": name, "email": email, **kwargs}
            logger.info(f"Created CRM contact (local): {contact['id']}")
            return contact
        except Exception as e:
            logger.error(f"Failed to create CRM contact: {str(e)}")
            raise

    def create_opportunity(self, name: str, amount: float, **kwargs) -> Dict[str, Any]:
        """Create an opportunity in the CRM. HubSpot owners may use Deals API."""
        if not self.authenticated:
            if not self.authenticate():
                raise RuntimeError("CRM authentication failed")

        try:

            if self.crm_type.lower() == "hubspot":
                if not self.session:
                    logger.warning("'requests' not available; returning mock HubSpot deal")
                    return {"id": f"deal_{hash(name) % 100000}", "properties": {"dealname": name, "amount": amount}}
                url = "https://api.hubapi.com/crm/v3/objects/deals"
                properties = {"dealname": name, "amount": str(amount)}
                properties.update(kwargs.get("properties", {}))
                payload = {"properties": properties}
                headers = {"Content-Type": "application/json"}
                resp = self.session.post(url, json=payload, headers=headers, timeout=10)
                if resp.status_code in (200, 201):
                    return resp.json()
                logger.error(f"HubSpot create_opportunity failed: {resp.status_code} {resp.text}")
                raise RuntimeError("HubSpot create_opportunity failed")

            opportunity = {"id": f"opp_{hash(name) % 100000}", "name": name, "amount": amount, "stage": "New", **kwargs}
            logger.info(f"Created CRM opportunity (local): {opportunity['id']}")
            return opportunity
        except Exception as e:
            logger.error(f"Failed to create CRM opportunity: {str(e)}")
            raise
