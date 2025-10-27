from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import db, schemas, crud, auth

router = APIRouter()

@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, database: Session = Depends(db.get_db)):
    existing_user = crud.get_user_by_email(database, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(database, user)

@router.post("/login")
def login(user: schemas.UserLogin, database: Session = Depends(db.get_db)):
    db_user = crud.get_user_by_email(database, user.email)
    if not db_user or not auth.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = auth.create_access_token({"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/user/me", response_model=schemas.UserResponse)
def get_current_user(token: str = Depends(auth.decode_token), database: Session = Depends(db.get_db)):
    user = crud.get_user_by_email(database, token)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user