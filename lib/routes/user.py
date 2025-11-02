import random
from fastapi import APIRouter, Depends, HTTPException, Header, status, Query
from sqlmodel import select
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from passlib.context import CryptContext
import json


from lib.config.database import get_async_session
from lib.models.sql import User
from lib.schemas import UserCreate, UserRead, UserUpdate, UserLogin
from pydantic import BaseModel
from lib.utils import create_access_token, verify_access_token, send_email

router = APIRouter(prefix="/users", tags=["Users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
MAX_BCRYPT_LENGTH = 72


# ==============================
# Schemas
# ==============================
class VerifyOtpRequest(BaseModel):
    email: str
    otp_code: str


class ResendOtpRequest(BaseModel):
    email: str


# ==============================
# Password helpers
# ==============================
def hash_password(password: str) -> str:
    if not password:
        raise HTTPException(status_code=400, detail="Password cannot be empty")
    if len(password.encode("utf-8")) > MAX_BCRYPT_LENGTH:
        password = password[:MAX_BCRYPT_LENGTH]
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    if len(plain_password.encode("utf-8")) > MAX_BCRYPT_LENGTH:
        plain_password = plain_password[:MAX_BCRYPT_LENGTH]
    return pwd_context.verify(plain_password, hashed_password)


# ==============================
# Auth helper
# ==============================
async def get_current_user(
    Authorization: Optional[str] = Header(None),
    session: AsyncSession = Depends(get_async_session),
):
    if not Authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        token = Authorization.replace("Bearer ", "")
        payload = verify_access_token(token)
        user_id = payload.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


# ==============================
# Register User — with OTP
# ==============================
# @router.post("/register", status_code=status.HTTP_201_CREATED)
# async def register_user(user_data: UserCreate, session: AsyncSession = Depends(get_async_session)):
#     """Register user and send OTP email only if role is 'user'."""
#     result = await session.execute(select(User).where(User.email == user_data.email))
#     existing_user = result.scalar_one_or_none()

#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")

#     hashed_pw = hash_password(user_data.password)
#     role = getattr(user_data, "role", "user")

#     otp_code = None
#     otp_verified = False
#     if role == "user":
#         otp_code = str(random.randint(100000, 999999))
#     else:
#         otp_verified = True

#     new_user = User(
#         name=user_data.name,
#         email=user_data.email,
#         password=hashed_pw,
#         role=role,
#         otp_verified=otp_verified,
#         otp_code=otp_code
#     )

#     session.add(new_user)
#     await session.commit()
#     await session.refresh(new_user)

#     # Send OTP for user only
#     if role == "user" and otp_code:
#         try:
#             subject = "Your OTP Verification Code"
#             body = f"Hello {new_user.name},\n\nYour OTP code is: {otp_code}\n\nIt will expire in 10 minutes."
#             html = f"""
#             <html>
#             <body style="font-family:sans-serif; color:#333">
#                 <h2>OTP Verification</h2>
#                 <p>Hello <b>{new_user.name}</b>,</p>
#                 <p>Your OTP code is:</p>
#                 <h3 style="color:#007BFF;">{otp_code}</h3>
#                 <p>This code will expire in 10 minutes.</p>
#             </body>
#             </html>
#             """
#             await send_email(subject=subject, recipients=[new_user.email], body=body, html=html)
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"Failed to send OTP email: {str(e)}")

#     return {
#         "message": (
#             "User registered successfully. Please verify OTP sent to your email."
#             if role == "user"
#             else "Account created successfully."
#         ),
#         "user_id": new_user.id,
#         "email": new_user.email,
#         "role": new_user.role,
#     }


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, session: AsyncSession = Depends(get_async_session)):
    """
    Register a new user.
    - user → generates and sends OTP for verification
    - counselor → generates a random password and emails it
    - admin → created directly without email/OTP
    """
    result = await session.execute(
        select(User).where(User.email == user_data.email, User.role == user_data.role)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered for this role")

    role = getattr(user_data, "role", "user")
    password_to_hash = user_data.password
    otp_code = None
    otp_verified = False

    # -------------------------
    #  USER ROLE → OTP Flow
    # -------------------------
    if role == "user":
        otp_code = str(random.randint(100000, 999999))
        otp_verified = False

    # -------------------------
    #  COUNSELOR ROLE → Random Password Flow
    # -------------------------
    elif role == "counselor":
        # generate random secure password
        random_password = "".join(
            random.choices("ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!@#$%", k=10)
        )
        password_to_hash = random_password
        otp_verified = True  # counselor auto-verified

        # send password email
        try:
            subject = "Your Counselor Account Credentials"
            body = (
                f"Hello {user_data.name},\n\n"
                f"Your counselor account has been created successfully.\n\n"
                f"Login Email: {user_data.email}\n"
                f"Password: {random_password}\n\n"
                f"Please log in and change your password after first login.\n\n"
                f"Regards,\nOral Cancer AI Team"
            )
            html = f"""
            <html>
            <body style="font-family:sans-serif; color:#333">
                <h2>Welcome to Oral Cancer AI Platform</h2>
                <p>Hello <b>{user_data.name}</b>,</p>
                <p>Your counselor account has been created successfully.</p>
                <p><b>Login Email:</b> {user_data.email}</p>
                <p><b>Temporary Password:</b> <span style="color:#007BFF;">{random_password}</span></p>
                <p>Please log in and change your password immediately.</p>
                <br/>
                <p>Regards,<br/>Oral Cancer AI Team</p>
            </body>
            </html>
            """
            await send_email(subject=subject, recipients=[user_data.email], body=body, html=html)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send counselor email: {str(e)}")

    # -------------------------
    #  ADMIN ROLE → Normal Create
    # -------------------------
    else:
        otp_verified = True  # admin auto-verified

    # -------------------------
    #  Final create & hash
    # -------------------------
    hashed_pw = hash_password(password_to_hash)

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_pw,
        role=role,
        otp_verified=otp_verified,
        otp_code=otp_code,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # -------------------------
    #  Send OTP for users
    # -------------------------
    if role == "user" and otp_code:
        try:
            subject = "Your OTP Verification Code"
            body = f"Hello {new_user.name},\n\nYour OTP code is: {otp_code}\n\nIt will expire in 10 minutes."
            html = f"""
            <html>
            <body style="font-family:sans-serif; color:#333">
                <h2>OTP Verification</h2>
                <p>Hello <b>{new_user.name}</b>,</p>
                <p>Your OTP code is:</p>
                <h3 style="color:#007BFF;">{otp_code}</h3>
                <p>This code will expire in 10 minutes.</p>
            </body>
            </html>
            """
            await send_email(subject=subject, recipients=[new_user.email], body=body, html=html)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send OTP email: {str(e)}")

    return {
        "message": (
            "User registered successfully. Please verify OTP sent to your email."
            if role == "user"
            else "Account created successfully and credentials sent via email."
        ),
        "user_id": new_user.id,
        "email": new_user.email,
        "role": new_user.role,
    }

# ==============================
# Verify OTP (JSON body)
# ==============================
@router.post("/verify-otp", status_code=status.HTTP_200_OK)
async def verify_otp(payload: VerifyOtpRequest, session: AsyncSession = Depends(get_async_session)):
    """Verify OTP and activate the user."""
    email = payload.email
    otp_code = payload.otp_code

    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.otp_verified:
        raise HTTPException(status_code=400, detail="User already verified")

    if not user.otp_code or user.otp_code != otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP code")

    user.otp_verified = True
    user.otp_code = None
    session.add(user)
    await session.commit()
    await session.refresh(user)

    token = create_access_token({"id": user.id, "email": user.email, "role": user.role})

    return {
        "message": "OTP verified successfully. Account activated.",
        "access_token": token,
        "user": UserRead.model_validate(user)
    }


# ==============================
# Resend OTP
# ==============================
@router.post("/resend-otp", status_code=status.HTTP_200_OK)
async def resend_otp(payload: ResendOtpRequest, session: AsyncSession = Depends(get_async_session)):
    """Resend a new OTP to unverified users."""
    email = payload.email
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.otp_verified:
        raise HTTPException(status_code=400, detail="User already verified")

    # Generate new OTP
    new_otp = str(random.randint(100000, 999999))
    user.otp_code = new_otp
    await session.commit()

    # Send new OTP
    try:
        subject = "Your New OTP Verification Code"
        body = f"Hello {user.name}, your new OTP code is: {new_otp}"
        html = f"""
        <html><body>
        <p>Hello <b>{user.name}</b>,</p>
        <p>Your new OTP is <b style='color:#007BFF;'>{new_otp}</b>.</p>
        </body></html>
        """
        await send_email(subject, [user.email], body, html=html)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP email: {str(e)}")

    return {"message": "New OTP sent successfully."}


# ==============================
# Login
# ==============================
@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(user_data: UserLogin, session: AsyncSession = Depends(get_async_session)):
    """Login with email and password (requires OTP verification for normal users)."""
    result = await session.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user.role == "user" and not user.otp_verified:
        raise HTTPException(
            status_code=403,
            detail="Account not verified. Please verify your OTP before logging in."
        )

    token = create_access_token({"id": user.id, "email": user.email, "role": user.role})

    return {
        "message": "Login successful",
        "user": UserRead.model_validate(user),
        "access_token": token
    }


# ==============================
# Get Current User (via Token)
# ==============================
@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    """Fetch user info using Bearer token"""
    return current_user


# ==============================
# Get All Users
# ==============================
@router.get("/")
async def list_users(
    session: AsyncSession = Depends(get_async_session),
    page: int = Query(1, ge=1, description="Page number, starts from 1"),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    filters: Optional[str] = Query(None, description="Filters as JSON string, e.g. {'role':'user'}"),
    orderby_col: Optional[str] = Query("created_at", description="Column to order by"),
    orderby_dir: Optional[str] = Query("desc", description="Order direction: asc or desc"),
):
    """
    List users with pagination, search, filtering, and ordering.
    """

    query = select(User)

    # ✅ Parse filters (string → dict)
    filter_dict = {}
    if filters:
        try:
            filter_dict = json.loads(filters)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in filters parameter")

    # ✅ Apply filters dynamically
    for key, value in filter_dict.items():
        if hasattr(User, key):
            query = query.where(getattr(User, key) == value)

    # ✅ Apply search
    if search:
        search_term = f"%{search.lower()}%"
        query = query.where(
            (User.name.ilike(search_term)) | (User.email.ilike(search_term))
        )

    # ✅ Apply ordering
    if hasattr(User, orderby_col):
        order_column = getattr(User, orderby_col)
        if orderby_dir.lower() == "asc":
            query = query.order_by(order_column.asc())
        else:
            query = query.order_by(order_column.desc())
    else:
        query = query.order_by(User.created_at.desc())

    # ✅ Pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    # ✅ Execute
    result = await session.execute(query)
    users = result.scalars().all()

    # ✅ Count total
    count_result = await session.execute(select(text("COUNT(*) FROM users")))
    total = count_result.scalar_one()

    # ✅ Return metadata + data
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total // limit) + (1 if total % limit else 0),
        "count": len(users),
        "data": [UserRead.model_validate(u) for u in users],
    }


# ==============================
# Get Single User by ID
# ==============================
@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, session: AsyncSession = Depends(get_async_session)):
    """Get user by ID"""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ==============================
# Update User
# ==============================
@router.put("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, user_data: UserUpdate, session: AsyncSession = Depends(get_async_session)):
    """Update user details"""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user_data.dict(exclude_unset=True).items():
        if key == "password" and value:
            value = hash_password(value)
        setattr(user, key, value)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# ==============================
# Delete User
# ==============================
@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, session: AsyncSession = Depends(get_async_session)):
    """Delete user by ID"""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await session.delete(user)
    await session.commit()
    return {"message": "User deleted successfully"}
