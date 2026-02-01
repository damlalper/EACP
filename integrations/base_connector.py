"""
Base connector class for enterprise integrations
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """Base class for all enterprise system connectors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.authenticated = False
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the enterprise system"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to the enterprise system"""
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """Get connector configuration"""
        return self.config
