from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from auth.resolver import CasbinResolver

router = APIRouter()

# Initialize resolver with file-backed configuration
resolver = CasbinResolver("config/casbin_resolvers.json")


class ContextModel(BaseModel):
    tenant: Optional[str] = Field(
        None, description="Tenant identifier used to resolve model/policy"
    )


class EnforceRequest(BaseModel):
    context: ContextModel
    sub: Any
    obj: Any
    act: Any


class PolicyMutationRequest(BaseModel):
    context: ContextModel
    sub: str
    obj: str
    act: str


@router.post("/enforce")
def enforce(req: EnforceRequest) -> Dict[str, bool]:
    """Evaluate whether the given subject/action on an object is allowed.

    Args:
        req: EnforceRequest containing `context`, `sub`, `obj`, and `act`.

    Returns:
        A dict with key "allowed" and a boolean indicating the decision.

    Raises:
        HTTPException: 404 if resolver lookup fails, 500 for other errors.
    """
    ctx = req.context.model_dump(exclude_none=True)
    try:
        wrapper = resolver.resolve(ctx)
        allowed = wrapper.enforce(req.sub, req.obj, req.act)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enforce error: {e}")
    return {"allowed": bool(allowed)}


@router.post("/policies")
def add_policy(req: PolicyMutationRequest) -> Dict[str, bool]:
    """Add a policy (sub, obj, act) for the resolved context and persist it.

    Args:
        req: PolicyMutationRequest containing `context`, `sub`, `obj`, and `act`.

    Returns:
        A dict with key "added" and a boolean indicating whether the policy
        was added.

    Raises:
        HTTPException: 404 if resolver lookup fails, 500 for other errors.
    """
    ctx = req.context.model_dump(exclude_none=True)
    try:
        wrapper = resolver.resolve(ctx)
        ok = wrapper.add_policy(req.sub, req.obj, req.act)
        if ok:
            wrapper.save_policy()
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Add policy error: {e}")
    return {"added": bool(ok)}


@router.delete("/policies")
def remove_policy(req: PolicyMutationRequest) -> Dict[str, bool]:
    """Remove a policy (sub, obj, act) for the resolved context and persist it.

    Args:
        req: PolicyMutationRequest containing `context`, `sub`, `obj`, and `act`.

    Returns:
        A dict with key "removed" and a boolean indicating whether the policy
        was removed.

    Raises:
        HTTPException: 404 if resolver lookup fails, 500 for other errors.
    """
    ctx = req.context.model_dump(exclude_none=True)
    try:
        wrapper = resolver.resolve(ctx)
        ok = wrapper.remove_policy(req.sub, req.obj, req.act)
        if ok:
            wrapper.save_policy()
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Remove policy error: {e}")
    return {"removed": bool(ok)}


@router.get("/policies")
def get_policies(tenant: Optional[str] = None) -> Dict[str, Any]:
    """Return all policies for the given tenant context.

    Args:
        tenant: Optional tenant identifier used to resolve model/policy.

    Returns:
        A dict with key "policies" containing a list of policy tuples/rows.

    Raises:
        HTTPException: 404 if resolver lookup fails, 500 for other errors.
    """
    ctx: Dict[str, Any] = {"tenant": tenant} if tenant is not None else {}
    try:
        wrapper = resolver.resolve(ctx)
        policies = wrapper.get_policies()
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Get policies error: {e}")
    return {"policies": policies}
