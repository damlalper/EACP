"""
Simple integration smoke test runner.
Reads `config.yaml` if present, initializes orchestrator and runs a small test for each configured integration.

Usage:
    python scripts/integration_smoketest.py

This script is tolerant to missing API keys and missing `requests` library — it will report skipped results.
"""
import os
import yaml
import logging
import sys
import os

# Ensure project root is on sys.path so `integrations` package can be imported
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from integrations import JiraConnector, AzureDevOpsConnector, CRMConnector, SAPConnector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smoketest")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def run():
    config = load_config()

    integrations_cfg = config.get("integrations", {})
    integrations = {}
    if "jira" in integrations_cfg:
        integrations["jira"] = JiraConnector(integrations_cfg["jira"])
    if "azure_devops" in integrations_cfg:
        integrations["azure_devops"] = AzureDevOpsConnector(integrations_cfg["azure_devops"])
    if "crm" in integrations_cfg:
        integrations["crm"] = CRMConnector(integrations_cfg["crm"])
    if "sap" in integrations_cfg:
        integrations["sap"] = SAPConnector(integrations_cfg["sap"])
    if not integrations:
        logger.info("No integrations configured. Update config.yaml with your integration settings.")
        return

    logger.info(f"Found integrations: {list(integrations.keys())}")

    # For each integration, run a representative call
    for name, connector in integrations.items():
        logger.info(f"Testing integration: {name}")
        try:
            if name == "jira":
                res = connector.create_ticket(title="Smoke Test", description="Smoke test created by EACP")
                logger.info(f"JIRA response: {res}")

            elif name == "azure_devops":
                res = connector.create_work_item(title="Smoke Test", description="Smoke test created by EACP")
                logger.info(f"Azure DevOps response: {res}")

            elif name == "crm":
                res = connector.create_contact(name="Smoke User", email="smoke@example.com")
                logger.info(f"CRM response: {res}")

            elif name == "sap":
                res = connector.execute_function(function_name="/ping", parameters={})
                logger.info(f"SAP response: {res}")

            else:
                logger.info(f"No smoke test defined for integration: {name}")

        except Exception as e:
            logger.error(f"Smoke test for {name} failed: {e}")


if __name__ == "__main__":
    run()
