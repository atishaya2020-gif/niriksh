from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session

from app.core.roles import ROLE_CAPABILITY_CEILINGS
from app.db.models import (
    User, Case, CaseGrant, CrossStateGrant, Jurisdiction,
    UserJurisdiction, CaseJurisdiction, CAPABILITIES, SAFE_CROSS_STATE_CAPABILITIES
)

# Capabilities inherited from a user's own (normal) jurisdiction membership.
# Distinct from the narrower cross-state safe baseline.
JURISDICTION_BASELINE_CAPABILITIES = {
    "case:view",
    "search:view",
    "match:view",
    "alert:view",
    "network:view",
    "analytics:view",
}

@dataclass
class AuthorizedScope:
    user_id: int
    role: str
    is_super_admin: bool
    global_capabilities: set[str] = field(default_factory=set)
    case_capabilities: dict[int, set[str]] = field(default_factory=dict)
    jurisdiction_ids: set[int] = field(default_factory=set)
    cross_state_jurisdiction_ids: set[int] = field(default_factory=set)
    cross_case_permitted: bool = False

def build_authorized_scope(session: Session, user: User) -> AuthorizedScope:
    is_super_admin = user.role == "SUPER_ADMIN"

    # 1. Resolve basic info
    scope = AuthorizedScope(
        user_id=user.id,
        role=user.role,
        is_super_admin=is_super_admin
    )

    if is_super_admin:
        scope.global_capabilities = set(CAPABILITIES)
        scope.cross_case_permitted = True
        return scope

    # 2. Jurisdiction associations
    jurisdictions = session.scalars(
        select(UserJurisdiction.jurisdiction_id).where(UserJurisdiction.user_id == user.id)
    ).all()
    scope.jurisdiction_ids = set(jurisdictions)

    # 3. Cross-state grants
    now = datetime.now(timezone.utc)
    cross_state = session.scalars(
        select(CrossStateGrant.target_jurisdiction_id).where(
            and_(
                CrossStateGrant.requesting_user_id == user.id,
                CrossStateGrant.status == "APPROVED",
                CrossStateGrant.revoked_at == None,
                or_(CrossStateGrant.expires_at == None, CrossStateGrant.expires_at > now)
            )
        )
    ).all()
    scope.cross_state_jurisdiction_ids = set(cross_state)

    # 4. Role ceiling capabilities (global)
    scope.global_capabilities = ROLE_CAPABILITY_CEILINGS.get(user.role, set())

    return scope

def get_case_capabilities(session: Session, user: User, case_id: int) -> set[str]:
    # 1. Role Ceiling
    ceiling = ROLE_CAPABILITY_CEILINGS.get(user.role, set())
    if user.role == "SUPER_ADMIN":
        ceiling = set(CAPABILITIES)

    # 2. Jurisdiction Inheritance (baseline)
    # Check if user has jurisdiction access to this case
    case_jurisdictions = session.scalars(
        select(CaseJurisdiction.jurisdiction_id).where(CaseJurisdiction.case_id == case_id)
    ).all()

    user_jurs = session.scalars(
        select(UserJurisdiction.jurisdiction_id).where(UserJurisdiction.user_id == user.id)
    ).all()

    has_jurisdiction_access = any(jur in set(user_jurs) for jur in case_jurisdictions)

    # Check Cross-state access
    now = datetime.now(timezone.utc)
    has_cross_state_access = session.query(CrossStateGrant).filter(
        CrossStateGrant.requesting_user_id == user.id,
        CrossStateGrant.target_jurisdiction_id.in_(case_jurisdictions),
        CrossStateGrant.status == "APPROVED",
        CrossStateGrant.revoked_at == None,
        or_(CrossStateGrant.expires_at == None, CrossStateGrant.expires_at > now)
    ).first() is not None

    effective = set()
    if has_jurisdiction_access:
        effective.update(JURISDICTION_BASELINE_CAPABILITIES)
    if has_cross_state_access:
        effective.update(SAFE_CROSS_STATE_CAPABILITIES)

    # 3. Explicit Case Grants
    grants = session.scalars(
        select(CaseGrant.capability).where(
            and_(
                CaseGrant.user_id == user.id,
                CaseGrant.case_id == case_id,
                CaseGrant.revoked_at == None,
                or_(CaseGrant.expires_at == None, CaseGrant.expires_at > now)
            )
        )
    ).all()
    effective.update(grants)

    # 4. Restrict by Role Ceiling
    return effective.intersection(ceiling)

def has_case_capability(session: Session, user: User, case_id: int, capability: str) -> bool:
    if user.role == "SUPER_ADMIN":
        return True
    return capability in get_case_capabilities(session, user, case_id)

def require_case_capability(session: Session, user: User, case_id: int, capability: str):
    if not has_case_capability(session, user, case_id, capability):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient capability: {capability}"
        )

def get_authorized_case(session: Session, user: User, case_id: int, capability: str) -> Case:
    case = session.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    # If user cannot even view the case, treat as 404 (hidden)
    if not has_case_capability(session, user, case_id, "case:view"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    # If they can view it, but lack the specific requested capability, raise 403
    require_case_capability(session, user, case_id, capability)
    return case


def authorize_resource_case(
    session: Session,
    user: User,
    resource_case_id: int | None,
    capability: str,
    resource_name: str,
) -> None:
    """Authorize access to a resource's owning case before returning or mutating it."""
    if resource_case_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource_name} not found")
    get_authorized_case(session, user, resource_case_id, capability)


def has_global_capability(user: User, capability: str) -> bool:
    if user.role == "SUPER_ADMIN":
        return True
    return capability in ROLE_CAPABILITY_CEILINGS.get(user.role, set())

def require_global_capability(user: User, capability: str):
    if not has_global_capability(user, capability):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient capability: {capability}"
        )



def can_correlate_cross_case(session: Session, user: User) -> bool:
    if user.role == "SUPER_ADMIN":
        return True
    return "cross_case:correlate" in ROLE_CAPABILITY_CEILINGS.get(user.role, set())

def get_authorized_case_ids(session: Session, user: User, capability: str) -> set[int]:
    if user.role == "SUPER_ADMIN":
        # For super admin, we return None to indicate "all" in our filters.
        # But for now, returning a sentinel might work.
        return set() # Caller should check is_super_admin

    now = datetime.now(timezone.utc)

    # 1. Start with jurisdiction-based access (only for safe capabilities)
    authorized_case_ids = set()
    # Jurisdiction membership baseline (read-oriented capabilities).
    user_jurs = session.scalars(
        select(UserJurisdiction.jurisdiction_id).where(UserJurisdiction.user_id == user.id)
    ).all()
    authorized_case_ids.update(session.scalars(
        select(CaseJurisdiction.case_id).where(CaseJurisdiction.jurisdiction_id.in_(user_jurs))
    ).all())

    if capability in SAFE_CROSS_STATE_CAPABILITIES:
        # Cross-state grants
        cross_state_jurs = session.scalars(
            select(CrossStateGrant.target_jurisdiction_id).where(
                and_(
                    CrossStateGrant.requesting_user_id == user.id,
                    CrossStateGrant.status == "APPROVED",
                    CrossStateGrant.revoked_at == None,
                    or_(CrossStateGrant.expires_at == None, CrossStateGrant.expires_at > now)
                )
            )
        ).all()

        authorized_case_ids.update(session.scalars(
            select(CaseJurisdiction.case_id).where(CaseJurisdiction.jurisdiction_id.in_(cross_state_jurs))
        ).all())

    # 2. Add cases with explicit grants for this capability
    grant_case_ids = set(session.scalars(
        select(CaseGrant.case_id).where(
            and_(
                CaseGrant.user_id == user.id,
                CaseGrant.capability == capability,
                CaseGrant.revoked_at == None,
                or_(CaseGrant.expires_at == None, CaseGrant.expires_at > now)
            )
        )
    ).all())

    authorized_case_ids.update(grant_case_ids)

    # 3. Restrict by Role Ceiling
    ceiling = ROLE_CAPABILITY_CEILINGS.get(user.role, set())
    if capability not in ceiling:
        return set()

    return authorized_case_ids
