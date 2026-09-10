from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.security import (
    get_current_user,
)

from app.db.models import User

from app.db.postgres import (
    get_db,
)


router = APIRouter(
    prefix="/admin",
    tags=["Administration"],
)


def require_admin(
    user: User
):

    role = str(
        user.role or ""
    ).lower()

    if role not in {
        "admin",
        "super_admin",
    }:
        raise HTTPException(
            status_code=403,
            detail=
                "Administrator access required.",
        )


@router.get("/users")
def list_users(
    db: Session = Depends(
        get_db
    ),

    user: User = Depends(
        get_current_user
    ),
):

    require_admin(user)

    users = (
        db.query(User)
        .order_by(
            User.id.asc()
        )
        .all()
    )

    return {

        "success": True,

        "data": {

            "users": [

                {
                    "id":
                        item.id,

                    "username":
                        item.username,

                    "role":
                        item.role,

                    "is_active":
                        item.is_active,

                    "created_at":
                        item.created_at,
                }

                for item in users
            ]
        },

        "message":
            "Users retrieved successfully.",
    }


@router.patch(
    "/users/{user_id}/status"
)
def update_user_status(
    user_id: int,

    payload: dict,

    db: Session = Depends(
        get_db
    ),

    user: User = Depends(
        get_current_user
    ),
):

    require_admin(user)

    target = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not target:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    status = str(
        payload.get(
            "status",
            ""
        )
    ).upper()

    if status == "ACTIVE":

        target.is_active = True

    elif status in {
        "SUSPENDED",
        "BLOCKED",
    }:

        target.is_active = False

    else:

        raise HTTPException(
            status_code=400,
            detail=
                "Invalid user status.",
        )

    db.commit()
    db.refresh(target)

    return {

        "success": True,

        "data": {

            "id":
                target.id,

            "status":
                "ACTIVE"
                if target.is_active
                else "SUSPENDED",
        },

        "message":
            "User status updated.",
    }


@router.patch(
    "/users/{user_id}/role"
)
def update_user_role(
    user_id: int,

    payload: dict,

    db: Session = Depends(
        get_db
    ),

    user: User = Depends(
        get_current_user
    ),
):

    require_admin(user)

    target = (
        db.query(User)
        .filter(
            User.id == user_id
        )
        .first()
    )

    if not target:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    role = str(
        payload.get(
            "role",
            ""
        )
    ).strip()

    if not role:
        raise HTTPException(
            status_code=400,
            detail="Role is required.",
        )

    target.role = role.lower()

    db.commit()
    db.refresh(target)

    return {

        "success": True,

        "data": {

            "id":
                target.id,

            "role":
                target.role,
        },

        "message":
            "User role updated.",
    }
