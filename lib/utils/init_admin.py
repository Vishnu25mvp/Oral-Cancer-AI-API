import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from passlib.context import CryptContext
from lib.models.sql import User, UserRole
from lib.config.database import get_async_session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMIN_DEFAULTS = {
    "name": "System Admin",
    "email": "admin@oralcancer.ai",
    "password": "Admin@123",
    "role": UserRole.admin,
}


async def create_default_admin(session: AsyncSession):
    """Create default admin user if not exists."""
    result = await session.execute(
        select(User).where(
            (User.email == ADMIN_DEFAULTS["email"]) & (User.role == UserRole.admin)
        )
    )
    existing_admin = result.scalar_one_or_none()

    if existing_admin:
        print("✅ Default admin already exists.")
        return existing_admin

    hashed_pw = pwd_context.hash(ADMIN_DEFAULTS["password"])

    new_admin = User(
        name=ADMIN_DEFAULTS["name"],
        email=ADMIN_DEFAULTS["email"],
        password=hashed_pw,
        role=UserRole.admin,
        otp_verified=True,  # admin doesn’t need OTP
    )

    session.add(new_admin)
    await session.commit()
    await session.refresh(new_admin)
    print(f"🚀 Default admin created successfully: {new_admin.email}")
    return new_admin


async def init_admin_user():
    """Initialize the admin account during app startup."""
    async for session in get_async_session():
        await create_default_admin(session)
        break  # only need one session instance


# ✅ Optional: Run directly for testing
if __name__ == "__main__":
    asyncio.run(init_admin_user())
