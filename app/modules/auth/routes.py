from fastapi import APIRouter, status

from app.core.response import success_response
from app.modules.auth.dependencies import AuthServiceDep
from app.modules.auth.schemas import LoginSchema, RegisterSchema

auth_routes = APIRouter(prefix="/auth", tags=["Auth"])


@auth_routes.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: RegisterSchema, auth_service: AuthServiceDep):
    user = await auth_service.register(data)
    return success_response(
        data=user,
        message="User registered successfully",
        status_code=status.HTTP_201_CREATED,
    )


@auth_routes.post("/login")
async def login(data: LoginSchema, auth_service: AuthServiceDep):
    user = await auth_service.login(data.email, data.password)
    return success_response(
        data=user,
        message="User logged in successfully",
        status_code=status.HTTP_200_OK,
    )


# @auth_routes.post("/verify-email")
# async def verify_email():
#     return {"message": "Email verified successfully"}


# @auth_routes.post("/resend-verification")
# async def resend_verification():
#     return {"message": "Verification email sent successfully"}


# @auth_routes.post("/forgot-password")
# async def forgot_password():
#     return {"message": "Password reset email sent successfully"}


# @auth_routes.post("/reset-password")
# async def reset_password():
#     return {"message": "Password reset successfully"}


# @auth_routes.post("/change-password")
# async def change_password():
#     return {"message": "Password changed successfully"}


# @auth_routes.post("/refresh-token")
# async def refresh_token():
#     return {"message": "Token refreshed successfully"}


# @auth_routes.post("/logout")
# async def logout():
#     return {"message": "User logged out successfully"}
