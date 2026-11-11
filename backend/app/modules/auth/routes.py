from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.modules.auth.dependencies import get_current_user
from backend.app.db.tenant import set_password_reset_context
from backend.app.modules.auth.password_resets import (
    EmailDeliveryUnavailable,
    PasswordResetService,
    hash_reset_token,
    send_password_reset_email,
)
from backend.app.modules.auth.schemas import (
    AuthResult,
    LoginRequest,
    OrganizationSummary,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
    TokenResult,
    UserRead,
    UserProfileUpdate,
)
from backend.app.modules.auth.security import create_access_token
from backend.app.modules.auth.services import AuthenticationService
from backend.app.modules.auth.models import PasswordReset
from backend.app.modules.users.models import User
from backend.app.schemas import api_response
from sqlalchemy import select

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> dict[str, object]:
    try:
        user, organization = AuthenticationService(db).register(
            email=payload.email,
            full_name=payload.full_name,
            password=payload.password,
            organization_name=payload.organization_name,
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists"
        ) from exc
    result = AuthResult(
        access_token=create_access_token(user.id),
        user=UserRead.model_validate(user),
        organization=OrganizationSummary.model_validate(organization),
    )
    return api_response(result.model_dump(mode="json"))


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict[str, object]:
    user = AuthenticationService(db).authenticate(email=payload.email, password=payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result = TokenResult(access_token=create_access_token(user.id))
    return api_response(result.model_dump())


@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
def request_password_reset(
    payload: PasswordResetRequest,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    try:
        token = PasswordResetService(db).request(payload.email)
        if token is not None:
            send_password_reset_email(payload.email, token)
    except EmailDeliveryUnavailable as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Password reset email delivery is temporarily unavailable",
        ) from exc
    return api_response(
        {"message": "If an account exists for that address, reset instructions will be sent."}
    )


@router.post("/password-reset/confirm")
def confirm_password_reset(
    payload: PasswordResetConfirm,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    if not PasswordResetService(db).confirm(payload.token, payload.password):
        raise HTTPException(status_code=400, detail="Reset link is invalid or expired")
    return api_response({"message": "Password updated. You can now sign in."})


@router.get("/me")
def read_me(current_user: User = Depends(get_current_user)) -> dict[str, object]:
    return api_response(UserRead.model_validate(current_user).model_dump(mode="json"))


@router.patch("/me")
def update_me(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    values = payload.model_dump(exclude_unset=True)
    if not values:
        raise HTTPException(status_code=422, detail="At least one field must be provided")
    for field, value in values.items():
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise HTTPException(status_code=422, detail=f"{field} cannot be blank")
        setattr(current_user, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email address is already in use") from exc
    db.refresh(current_user)
    return api_response(UserRead.model_validate(current_user).model_dump(mode="json"))
