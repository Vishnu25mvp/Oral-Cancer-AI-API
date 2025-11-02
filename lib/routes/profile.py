from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List

from lib.config.database import get_async_session
from lib.models.sql import Profile, User
from lib.schemas import ProfileCreate, ProfileRead, ProfileUpdate
from lib.routes.user import get_current_user  

router = APIRouter(prefix="/profiles", tags=["Profiles"])


# =========================================
# CREATE PROFILE
# =========================================
@router.post("/", response_model=ProfileRead, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Create a new profile for the logged-in user."""
    existing = await session.execute(select(Profile).where(Profile.user_id == current_user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Profile already exists for this user")

    profile = Profile(user_id=current_user.id, **profile_data.dict(exclude_unset=True))
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


# =========================================
# GET OR CREATE MY PROFILE
# =========================================
@router.get("/me", response_model=ProfileRead)
async def get_or_create_my_profile(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    ✅ Fetches the current user's profile.
    🧩 If not found, auto-creates a blank one.
    """
    result = await session.execute(select(Profile).where(Profile.user_id == current_user.id))
    profile = result.scalar_one_or_none()

    if not profile:
        profile = Profile(user_id=current_user.id)
        session.add(profile)
        await session.commit()
        await session.refresh(profile)

    return profile


# =========================================
# GET ALL PROFILES (Admin only)
# =========================================
@router.get("/", response_model=List[ProfileRead])
async def list_profiles(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Admin-only: list all user profiles."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    result = await session.execute(select(Profile))
    profiles = result.scalars().all()
    return profiles


# =========================================
# UPDATE PROFILE
# =========================================
@router.put("/{profile_id}", response_model=ProfileRead)
async def update_profile(
    user_id: int,
    data: ProfileUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    Update a profile (self or admin).
    If profile not found → auto-create a new one for current user.
    """
    result = await session.execute(select(Profile).where(Profile.user_id == user_id))
    profile = result.scalar_one_or_none()

    # ============================
    # AUTO-CREATE IF NOT FOUND
    # ============================
    if not profile:
        profile = Profile(
            user_id=user_id,  # optional; SQLModel will auto-generate if not used
            **data.dict(exclude_unset=True)
        )
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        return profile

    # ============================
    # AUTHORIZATION
    # ============================
    if profile.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")

    # ============================
    # UPDATE EXISTING FIELDS
    # ============================
    for key, value in data.dict(exclude_unset=True).items():
        setattr(profile, key, value)

    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


# =========================================
# DELETE PROFILE
# =========================================
@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Delete a profile (self or admin)."""
    result = await session.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if profile.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this profile")

    await session.delete(profile)
    await session.commit()
    return None
