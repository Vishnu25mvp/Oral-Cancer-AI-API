import os, random, string, shutil
import numpy as np
from typing import List, Optional
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    status,
    Query
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from pathlib import Path
from sqlalchemy import text
import shutil, os

from lib.config.database import get_async_session
from lib.models.sql import User, Result
from lib.schemas import ResultRead, ResultCreate, PaginatedResultResponse
from lib.utils import send_email, hash_password, predict_image
from lib.routes.user import get_current_user

router = APIRouter(prefix="/results", tags=["Results"])

UPLOAD_DIR = Path("uploads/results")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# =========================================
# CREATE RESULT ENTRY (auto-create user)
# =========================================
# @router.post("/", response_model=ResultRead, status_code=status.HTTP_201_CREATED)
# async def create_result_entry(
#     email: str = Form(...),
#     name: str = Form("Unknown User"),
#     age: Optional[int] = Form(None),
#     gender: Optional[str] = Form(None),
#     files: List[UploadFile] = File(...),
#     session: AsyncSession = Depends(get_async_session),
#     current_user: User = Depends(get_current_user),
# ):
#     """
#     ✅ Create result entry.
#     - If user doesn't exist → auto-create and email credentials
#     - Saves uploaded images in /uploads/results/<user_id>/
#     - Stores created_by = logged-in user id
#     """

#     # 1️⃣ Check or create user
#     result = await session.execute(select(User).where(User.email == email))
#     user = result.scalar_one_or_none()

#     if not user:
#         random_password = "".join(random.choices(string.ascii_letters + string.digits, k=10))
#         hashed_pw = hash_password(random_password)
#         user = User(name=name, email=email, password=hashed_pw, role="user", otp_verified=True)
#         session.add(user)
#         await session.commit()
#         await session.refresh(user)

#         try:
#             subject = "Your Oral Cancer AI Account"
#             body = f"""
# Hello {name},

# An account has been created for you on the Oral Cancer AI Platform.

# 🔹 Email: {email}
# 🔹 Temporary Password: {random_password}

# Please log in and change your password after first login.

# Regards,  
# Oral Cancer AI Team
# """
#             await send_email(subject, [email], body)
#         except Exception as e:
#             print(f"⚠️ Failed to send email: {e}")

#     # 2️⃣ Save images
#     user_folder = UPLOAD_DIR / str(user.id)
#     user_folder.mkdir(parents=True, exist_ok=True)

#     saved_paths = []
#     for file in files:
#         filename = f"{user.id}_{file.filename}"
#         file_path = user_folder / filename
#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
#         saved_paths.append(str(file_path))

#     # 3️⃣ Create result
#     new_result = Result(
#         user_id=user.id,
#         created_by=current_user.id,
#         age=age,
#         gender=gender,
#         result=None,
#         confidence=None,
#         images=saved_paths,
#     )

#     session.add(new_result)
#     await session.commit()
#     await session.refresh(new_result)

#     return new_result


@router.post("/", response_model=ResultRead, status_code=status.HTTP_201_CREATED)
async def create_result_entry(
    email: str = Form(...),
    name: str = Form("Unknown User"),
    age: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    ✅ Create result entry with ML predictions.
    - Saves all uploaded oral images.
    - Predicts each with ML model.
    - Calculates average confidence & final label.
    """

    # 1️⃣ Check or create user
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        random_password = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        hashed_pw = hash_password(random_password)
        user = User(name=name, email=email, password=hashed_pw, role="user", otp_verified=True)
        session.add(user)
        await session.commit()
        await session.refresh(user)

        try:
            subject = "Your Oral Cancer AI Account"
            body = f"""
Hello {name},

An account has been created for you on the Oral Cancer AI Platform.

🔹 Email: {email}
🔹 Temporary Password: {random_password}

Please log in and change your password after first login.

Regards,  
Oral Cancer AI Team
"""
            await send_email(subject, [email], body)
        except Exception as e:
            print(f"⚠️ Email send failed: {e}")

    # 2️⃣ Save images
    user_folder = UPLOAD_DIR / str(user.id)
    user_folder.mkdir(parents=True, exist_ok=True)

    saved_paths = []
    predictions = []
    confidences = []

    for file in files:
        filename = f"{user.id}_{file.filename}"
        file_path = user_folder / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_paths.append(str(file_path))

        # 🔮 Predict with model
        label, conf = predict_image(str(file_path))
        predictions.append(label)
        confidences.append(conf)

    # 3️⃣ Calculate overall result
    avg_conf = round(float(np.mean(confidences)) * 100, 2)
    cancer_votes = predictions.count("CANCER")
    non_cancer_votes = predictions.count("NON CANCER")
    final_result = "CANCER" if cancer_votes > non_cancer_votes else "NON CANCER"

    # 4️⃣ Save result entry in DB
    new_result = Result(
        user_id=user.id,
        created_by=current_user.id,
        age=age,
        gender=gender,
        result=final_result,
        confidence=avg_conf,
        images=saved_paths,
    )

    session.add(new_result)
    await session.commit()
    await session.refresh(new_result)

    return new_result


# =========================================
# GET RESULTS — Role Based Filtering
# =========================================
@router.get("/")
async def get_results(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Number of records per page"),
    search: Optional[str] = Query(None, description="Search by gender or user email"),
    filters: Optional[str] = Query(None, description="JSON filters (e.g. {'gender':'Male'})"),
    orderby_col: Optional[str] = Query("date", description="Order by column"),
    orderby_dir: Optional[str] = Query("desc", description="Order direction: asc or desc"),
):
    """
    ✅ Get Results with:
    - Pagination
    - Search
    - Dynamic filters
    - Ordering
    - Role-based access control
    """

    # ==========================================
    # Base query + Join with User
    # ==========================================
    query = select(Result, User).join(User, User.id == Result.user_id)

    # ==========================================
    # 🔐 Role-based filter
    # ==========================================
    if current_user.role == "counselor":
        query = query.where(Result.created_by == current_user.id)
    elif current_user.role == "user":
        query = query.where(Result.user_id == current_user.id)
    # Admin → sees all

    # ==========================================
    # 🔍 Search
    # ==========================================
    if search:
        search_term = f"%{search.lower()}%"
        query = query.where(
            or_(
                User.email.ilike(search_term),
                User.name.ilike(search_term),
                Result.gender.ilike(search_term),
            )
        )

    # ==========================================
    # ⚙️ Filters (JSON)
    # ==========================================
    if filters:
        try:
            filter_dict = json.loads(filters)
            for key, value in filter_dict.items():
                if hasattr(Result, key):
                    query = query.where(getattr(Result, key) == value)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in filters parameter")

    # ==========================================
    # ↕️ Ordering
    # ==========================================
    if hasattr(Result, orderby_col):
        order_col = getattr(Result, orderby_col)
        query = query.order_by(order_col.asc() if orderby_dir.lower() == "asc" else order_col.desc())
    else:
        query = query.order_by(Result.date.desc())

    # ==========================================
    # 🧮 Total count (respecting filters)
    # ==========================================
    count_query = select(text("COUNT(*)")).select_from(Result)
    total = (await session.execute(count_query)).scalar() or 0

    # ==========================================
    # 📄 Pagination
    # ==========================================
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    # ==========================================
    # 🚀 Execute Query
    # ==========================================
    result = await session.execute(query)
    rows = result.all()

    # ==========================================
    # 🧩 Format Response
    # ==========================================
    data = []
    for res, user in rows:
        data.append({
            "id": res.id,
            "user_id": res.user_id,
            "created_by": res.created_by,
            "age": res.age,
            "gender": res.gender,
            "result": res.result,
            "confidence": res.confidence,
            "images": res.images,
            "date": res.date,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
            },
        })

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total // limit) + (1 if total % limit else 0),
        "count": len(data),
        "data": data,
    }
# =========================================
# GET RESULT BY ID (with permissions)
# =========================================
@router.get("/{result_id}")
async def get_result_by_id(
    result_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """
    ✅ Fetch a single result by ID
    Includes user info and enforces role-based access.
    """

    # ==========================================
    # 🚀 Fetch with JOIN (Result + User)
    # ==========================================
    query = (
        select(Result, User)
        .join(User, User.id == Result.user_id)
        .where(Result.id == result_id)
    )
    result = await session.execute(query)
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Result not found")

    result_obj, user_obj = row

    # ==========================================
    # 🔐 Role-based Access Control
    # ==========================================
    if current_user.role == "user" and result_obj.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if current_user.role == "counselor" and result_obj.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # ==========================================
    # 🧩 Format and Return Dict
    # ==========================================
    return {
        "id": result_obj.id,
        "user_id": result_obj.user_id,
        "created_by": result_obj.created_by,
        "age": result_obj.age,
        "gender": result_obj.gender,
        "result": result_obj.result,
        "confidence": result_obj.confidence,
        "images": result_obj.images,
        "date": result_obj.date,
        "user": {
            "id": user_obj.id,
            "name": user_obj.name,
            "email": user_obj.email,
        },
    }

# =========================================
# UPDATE RESULT (Admin or Owner Counselor)
# =========================================
@router.put("/{result_id}", response_model=ResultRead)
async def update_result(
    result_id: int,
    data: ResultCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Update result info (age, gender, result, confidence, etc)."""
    result = await session.get(Result, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    # Role check
    if current_user.role == "user":
        raise HTTPException(status_code=403, detail="Users cannot edit results")
    if current_user.role == "counselor" and result.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own results")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(result, key, value)

    session.add(result)
    await session.commit()
    await session.refresh(result)
    return result


# =========================================
# DELETE RESULT (Admin or Counselor who created it)
# =========================================
@router.delete("/{result_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_result(
    result_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user),
):
    """Delete a result entry based on role and ownership."""
    result = await session.get(Result, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    # Access rules
    if current_user.role == "user":
        raise HTTPException(status_code=403, detail="Users cannot delete results")
    if current_user.role == "counselor" and result.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own results")

    # Delete files from storage
    for img in result.images or []:
        try:
            os.remove(img)
        except FileNotFoundError:
            pass

    await session.delete(result)
    await session.commit()
    return None
