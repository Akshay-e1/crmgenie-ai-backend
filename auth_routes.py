from fastapi import APIRouter, HTTPException
from database import users_collection

from schemas import (
    RegisterUser,
    LoginUser
)

from auth import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter()


# ==========================
# REGISTER
# ==========================
@router.post("/register")
def register(user: RegisterUser):

    try:
        print("REGISTER REQUEST:", user)

        # Check if email already exists
        existing_user = users_collection.find_one(
            {"email": user.email}
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # Hash password
        hashed_password = hash_password(
            user.password
        )

        print("PASSWORD HASHED")

        # Create user document
        new_user = {
            "name": user.name,
            "phone": user.phone,
            "id_number": user.id_number,
            "age": user.age,
            "company": user.company,
            "email": user.email,
            "password": hashed_password
        }

        # Insert into MongoDB
        result = users_collection.insert_one(
            new_user
        )

        print("USER INSERTED:", result.inserted_id)

        return {
            "message": "User registered successfully",
            "user_id": str(result.inserted_id)
        }

    except HTTPException:
        raise

    except Exception as e:
        print("REGISTER ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================
# LOGIN
# ==========================
@router.post("/login")
def login(user: LoginUser):

    try:

        print("LOGIN REQUEST:", user.email)

        existing_user = users_collection.find_one(
            {"email": user.email}
        )

        if not existing_user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        valid_password = verify_password(
            user.password,
            existing_user["password"]
        )

        if not valid_password:
            raise HTTPException(
                status_code=401,
                detail="Invalid password"
            )

        token = create_access_token(
            {
                "user_id": str(existing_user["_id"]),
                "email": existing_user["email"]
            }
        )

        print("LOGIN SUCCESS")

        return {
            "message": "Login successful",
            "token": token,
            "name": existing_user["name"],
            "email": existing_user["email"],
            "id_number": existing_user["id_number"]
        }

    except HTTPException:
        raise

    except Exception as e:
        print("LOGIN ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )