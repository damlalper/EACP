"""
API Gateway for EACP
Provides request validation, rate limiting, authentication, and routing
"""

from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, rate: int = 100, period: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            rate: Number of requests allowed
            period: Time period in seconds
        """
        self.rate = rate
        self.period = period
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client."""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.period)
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff
        ]
        
        # Check if under limit
        if len(self.requests[client_id]) < self.rate:
            self.requests[client_id].append(now)
            return True
        
        return False
    
    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client."""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.period)
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > cutoff
        ]
        
        return self.rate - len(self.requests[client_id])


class APIGateway:
    """API Gateway with rate limiting, authentication, and request routing."""
    
    def __init__(self, rate_limit: int = 100, rate_period: int = 60):
        self.rate_limiter = RateLimiter(rate=rate_limit, period=rate_period)
        self.routes = {}
        self.middleware = []
        self.authenticated_tokens = set()
        logger.info(f"API Gateway initialized: {rate_limit} requests per {rate_period}s")
    
    def register_route(self, path: str, handler: Callable, methods: list = None):
        """Register a route handler."""
        methods = methods or ["GET", "POST"]
        for method in methods:
            key = f"{method}:{path}"
            self.routes[key] = handler
        logger.info(f"Route registered: {path} -> {handler.__name__}")
    
    def add_middleware(self, middleware: Callable):
        """Add middleware function."""
        self.middleware.append(middleware)
        logger.info(f"Middleware added: {middleware.__name__}")
    
    def register_token(self, token: str):
        """Register an authentication token."""
        self.authenticated_tokens.add(token)
        logger.debug(f"Token registered: {token[:10]}...")
    
    def authenticate(self, token: Optional[str]) -> bool:
        """Authenticate request with token."""
        if not token:
            return False
        return token in self.authenticated_tokens
    
    def handle_request(self, method: str, path: str, data: Dict[str, Any] = None,
                      token: Optional[str] = None, client_id: str = "default") -> Dict[str, Any]:
        """
        Handle incoming request with validation and rate limiting.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            data: Request payload
            token: Authentication token
            client_id: Client identifier for rate limiting
            
        Returns:
            Response dict with status, data, and metadata
        """
        
        # Rate limiting
        if not self.rate_limiter.is_allowed(client_id):
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return {
                "status": 429,
                "error": "Too many requests",
                "remaining_requests": 0
            }
        
        # Authentication
        if not self.authenticate(token):
            logger.warning(f"Authentication failed for client: {client_id}")
            return {
                "status": 401,
                "error": "Unauthorized"
            }
        
        # Find route handler
        route_key = f"{method}:{path}"
        handler = self.routes.get(route_key)
        
        if not handler:
            logger.warning(f"Route not found: {route_key}")
            return {
                "status": 404,
                "error": f"Route not found: {path}"
            }
        
        # Execute middleware
        for mw in self.middleware:
            try:
                mw(method, path, data)
            except Exception as e:
                logger.error(f"Middleware error: {str(e)}")
                return {
                    "status": 500,
                    "error": f"Middleware error: {str(e)}"
                }
        
        # Execute handler
        try:
            result = handler(data or {})
            return {
                "status": 200,
                "data": result,
                "timestamp": datetime.now().isoformat(),
                "remaining_requests": self.rate_limiter.get_remaining(client_id)
            }
        except Exception as e:
            logger.error(f"Handler error: {str(e)}")
            return {
                "status": 500,
                "error": f"Internal server error: {str(e)}"
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get gateway metrics."""
        return {
            "total_routes": len(self.routes),
            "middleware_count": len(self.middleware),
            "authenticated_tokens": len(self.authenticated_tokens)
        }


# Example middleware functions
def validate_payload(method: str, path: str, data: Optional[Dict]):
    """Middleware: Validate request payload."""
    if method == "POST" and not data:
        raise ValueError("POST requests require payload")


def log_request(method: str, path: str, data: Optional[Dict]):
    """Middleware: Log all requests."""
    logger.debug(f"Request: {method} {path}")


def rate_limit_decorator(rate_limiter: RateLimiter, client_id: str = "default"):
    """Decorator for rate limiting individual functions."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not rate_limiter.is_allowed(client_id):
                raise RuntimeError("Rate limit exceeded")
            return func(*args, **kwargs)
        return wrapper
    return decorator
