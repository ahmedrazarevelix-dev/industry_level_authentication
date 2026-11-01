from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.db.models import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schema.auth import (
    ChangePasswordRequest,
    DeleteAccountRequest,
    LoginRequest,
    RegisterRequest,
)

async def register_user(data: RegisterRequest, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == data.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def login_user(data: LoginRequest, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if (
        not user
        or not user.is_active
        or not verify_password(data.password, user.hashed_password)
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

async def change_user_password(
    user: User, data: ChangePasswordRequest, db: AsyncSession
):
    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.hashed_password = hash_password(data.new_password)
    await db.commit()
    return {"message": "Password changed successfully"}

async def delete_user_account(
    user: User, data: DeleteAccountRequest, db: AsyncSession
):
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Password is incorrect")
    await db.delete(user)
    await db.commit()
    return {"message": "Account deleted successfully"}
