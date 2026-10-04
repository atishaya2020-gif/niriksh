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
