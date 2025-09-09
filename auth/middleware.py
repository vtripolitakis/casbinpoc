from __future__ import annotations
import functools
import inspect
from typing import Any, Callable, Dict, Optional
from fastapi import HTTPException, Request
from auth.enforcer import CasbinEnforcer


class CasbinMiddleware:
    def __init__(self, model_path: str = "auth/models/rbac_model.conf", 
                 policy_path: str = "auth/policies/rbac_policy.csv"):
        self.enforcer = CasbinEnforcer(model_path, policy_path)
    
    def check_permission(self, sub: str, obj: str, act: str) -> bool:
        """Check if the subject has permission to perform the action on the object"""
        return self.enforcer.enforce(sub, obj, act)


# Global middleware instance
middleware = CasbinMiddleware()


def requires(action: str, resource: Optional[str] = None):
    """
    Decorator that enforces Casbin authorization for FastAPI endpoints.
    
    Args:
        action: The action to check (e.g., 'read', 'write', 'delete')
        resource: The resource to check against (optional, defaults to endpoint path)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # Look for request in kwargs
                request = kwargs.get('request')
            
            if not request:
                raise HTTPException(status_code=500, detail="Request object not found")
            
            # Extract user from headers (you can modify this based on your auth system)
            user = request.headers.get('X-User-ID', 'anonymous')
            
            # Use provided resource or default to the endpoint path
            target_resource = resource or request.url.path
            
            # Check permission
            if not middleware.check_permission(user, target_resource, action):
                raise HTTPException(
                    status_code=403, 
                    detail=f"Access denied: {user} cannot {action} {target_resource}"
                )
            
            return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # Look for request in kwargs
                request = kwargs.get('request')
            
            if not request:
                raise HTTPException(status_code=500, detail="Request object not found")
            
            # Extract user from headers (you can modify this based on your auth system)
            user = request.headers.get('X-User-ID', 'anonymous')
            
            # Use provided resource or default to the endpoint path
            target_resource = resource or request.url.path
            
            # Check permission
            if not middleware.check_permission(user, target_resource, action):
                raise HTTPException(
                    status_code=403, 
                    detail=f"Access denied: {user} cannot {action} {target_resource}"
                )
            
            return func(*args, **kwargs)
        
        # Check if the function is async or sync
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
