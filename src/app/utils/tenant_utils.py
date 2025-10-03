from fastapi import HTTPException, status
from typing import Sequence, Callable, Any

def assert_tenant_access(user: dict, resource_hostel_id: int):
    """
    Enforce that the current_user can access a resource belonging to a hostel.
    - super_admin: always allowed
    - hostel_admin/tenant: only if user.hostel_id == resource_hostel_id
    """
    roles = user.get("roles", [])
    if "super_admin" in roles:
        return
    if str(user.get("hostel_id")) != str(resource_hostel_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User cannot access resources of another hostel",
        )

def filter_tenant_records(user: dict, records: Sequence[Any], tenant_id_attr: str = "tenant_id"):
    """
    Restrict a collection of records based on tenant ownership.
    - super_admin / hostel_admin: return all records
    - tenant: return only records where record.tenant_id == user.id
    """
    roles = user.get("roles", [])
    if "tenant" in roles:
        return [rec for rec in records if getattr(rec, tenant_id_attr, None) == user["id"]]
    return records

def tenant_scoped_filter_query(user: dict, base_query, model, tenant_id_field: str = "tenant_id"):
    """
    For ORM queries: restrict tenant access at query level.
    Example:
        q = select(Invoice)
        q = tenant_scoped_filter_query(user, q, Invoice)
        rows = (await session.execute(q)).scalars().all()
    """
    from sqlalchemy import and_

    roles = user.get("roles", [])
    if "tenant" in roles:
        q = base_query.where(getattr(model, tenant_id_field) == user["id"])
        return q
    return base_query