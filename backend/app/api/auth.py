import hashlib
from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import User, Role
from backend.app.schemas.schemas import Token, LoginRequest, UserOut
from backend.app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

def hash_password(password: str) -> str:
    salt = "agentic_invoice_ai_salt"
    return hashlib.sha256((salt + password).encode("utf-8")).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    if not token:
        # Default to admin user in demo mode if no token provided
        admin_user = db.query(User).filter(User.email == "admin@enterprise.ai").first()
        if admin_user:
            return admin_user
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role.name})
    user_out = UserOut(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.name,
        is_active=user.is_active
    )
    return Token(access_token=access_token, token_type="bearer", user=user_out)

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.name,
        is_active=current_user.is_active
    )

@router.post("/switch-role/{role_name}", response_model=Token)
def switch_demo_role(role_name: str, db: Session = Depends(get_db)):
    """Allow immediate role switching in UI to demonstrate role-based access control."""
    user = db.query(User).join(Role).filter(Role.name == role_name.lower()).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"No demo user found with role '{role_name}'")
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role.name})
    user_out = UserOut(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.name,
        is_active=user.is_active
    )
    return Token(access_token=access_token, token_type="bearer", user=user_out)
