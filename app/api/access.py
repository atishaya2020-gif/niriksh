from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.core.security import (
    get_current_user,
)

from app.db.models import (
    AccessRequest,
    User,
)

from app.db.postgres import (
    get_db,
)


router = APIRouter(
    prefix="/access",
    tags=["Access Requests"],
)


@router.post("/request")
def request_access(
    payload: dict,

    db: Session = Depends(
        get_db
    ),
):

    username = str(
        payload.get(
            "username",
            ""
        )
    ).strip()

    if not username:

        raise HTTPException(
            status_code=400,
            detail=
                "Username is required.",
        )

    existing = (
        db.query(
            AccessRequest
        )
        .filter(
            AccessRequest.username ==
            username
        )
        .filter(
            AccessRequest.status ==
            "PENDING"
        )
        .first()
    )

    if existing:

        return {
            "success": False,

            "message":
                "An access request is already pending."
        }

    request = AccessRequest(

        username=
            username,

        requested_role=
            str(
                payload.get(
                    "requested_role",
                    "investigator"
                )
            ),

        department=
            payload.get(
                "department"
            ),

        reason=
            payload.get(
                "reason"
            ),

        status=
            "PENDING",
    )

    db.add(request)

    db.commit()

    db.refresh(request)

    return {

        "success": True,

        "data": {

            "id":
                request.id,

            "username":
                request.username,

            "status":
                request.status,
        },

        "message":
            "Access request submitted.",
    }


@router.get("/requests")
def list_access_requests(

    db: Session = Depends(
        get_db
    ),

    user: User = Depends(
        get_current_user
    ),
):

    if str(
        user.role
    ).lower() not in {
        "admin",
        "super_admin",
    }:

        raise HTTPException(
            status_code=403,
            detail=
                "Administrator access required.",
        )

    requests = (
        db.query(
            AccessRequest
        )
        .order_by(
            AccessRequest.created_at.desc()
        )
        .all()
    )

    return {

        "success": True,

        "data": {

            "requests": [

                {

                    "id":
                        item.id,

                    "username":
                        item.username,

                    "requested_role":
                        item.requested_role,

                    "department":
                        item.department,

                    "reason":
                        item.reason,

                    "status":
                        item.status,

                    "created_at":
                        item.created_at,
                }

                for item in requests
            ]
        },
    }


@router.patch(
    "/requests/{request_id}"
)
def update_access_request(

    request_id: int,

    payload: dict,

    db: Session = Depends(
        get_db
    ),

    user: User = Depends(
        get_current_user
    ),
):

    if str(
        user.role
    ).lower() not in {
        "admin",
        "super_admin",
    }:

        raise HTTPException(
            status_code=403,
            detail=
                "Administrator access required.",
        )

    request = (
        db.query(
            AccessRequest
        )
        .filter(
            AccessRequest.id ==
            request_id
        )
        .first()
    )

    if not request:

        raise HTTPException(
            status_code=404,
            detail=
                "Access request not found.",
        )

    status = str(
        payload.get(
            "status",
            ""
        )
    ).upper()

    if status not in {
        "APPROVED",
        "REJECTED",
        "PENDING",
    }:

        raise HTTPException(
            status_code=400,
            detail=
                "Invalid request status.",
        )

    request.status = status

    db.commit()

    db.refresh(request)

    return {

        "success": True,

        "data": {

            "id":
                request.id,

            "status":
                request.status,
        },

        "message":
            "Access request updated.",
    }
