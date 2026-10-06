from app.db.models import CAPABILITIES

ROLE_CAPABILITY_CEILINGS = {
    "SUPER_ADMIN": set(CAPABILITIES),
    "ADMIN": set(CAPABILITIES),
    "SENIOR_INVESTIGATOR": {
        "case:view", "case:create", "case:update", "case:ingest",
        "evidence:create", "evidence:verify",
        "alert:view", "alert:manage",
        "match:view", "match:review",
        "processing:start", "processing:retry",
        "network:view", "analytics:view", "search:view",
        "cross_case:correlate"
    },
    "INVESTIGATOR": {
        "case:view", "case:create", "case:update", "case:ingest",
        "evidence:create", "evidence:verify",
        "alert:view", "alert:manage",
        "match:view", "match:review",
        "search:view"
    },
    "ANALYST": {
        "alert:view", "network:view", "analytics:view", "search:view",
        "match:view"
    },
    "STATE_OFFICER": {
        "case:view", "search:view", "alert:view"
    },
    "VIEWER": {
        "case:view", "search:view"
    }
}

VALID_ROLES = set(ROLE_CAPABILITY_CEILINGS.keys())
UNKNOWN_ROLE = "UNKNOWN"


def normalize_role(raw_role) -> str:
    """Normalize a role string to its canonical uppercase form.

    - "admin" -> "ADMIN"
    - " super_admin " -> "SUPER_ADMIN"
    - unknown or empty -> "UNKNOWN" (no capabilities)
    """
    if raw_role is None:
        return UNKNOWN_ROLE
    normalized = str(raw_role).strip().upper()
    if normalized in ROLE_CAPABILITY_CEILINGS:
        return normalized
    return UNKNOWN_ROLE
