from fastapi import APIRouter, Depends

from app.dependencies import get_auth_service, get_current_user
from app.schemas.auth import CurrentUser, LoginRequest, LoginResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, auth: AuthService = Depends(get_auth_service)) -> LoginResponse:
    return auth.login(body)


@router.get("/me", response_model=CurrentUser)
def me(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    return user
