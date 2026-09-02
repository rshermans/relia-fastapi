from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
import uuid

from backend.app.database.session import get_db
from backend.app.database.models import Usuario
from backend.app.schemas.schemas import UserCreate, UserResponse, UserUpdate, LoginRequest, Token
from backend.app.config import settings

router = APIRouter(prefix="/auth", tags=["Autenticação & Usuários"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__truncate_error=True)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def _safe_password(password: str) -> str:
    """Trunca a password a 72 bytes (limite bcrypt) para compatibilidade com bcrypt >=4.1."""
    return password.encode("utf-8")[:72].decode("utf-8", errors="ignore")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais de autenticação inválidas ou expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(Usuario).filter(Usuario.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(Usuario).filter(Usuario.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Este e-mail já se encontra registado.")
    
    hashed_pwd = pwd_context.hash(_safe_password(user_in.password))
    user = Usuario(
        uid=f"usr-{uuid.uuid4().hex[:8]}",
        nome=user_in.nome,
        email=user_in.email,
        hashed_password=hashed_pwd,
        idade=user_in.idade,
        cidade=user_in.cidade,
        interesses=user_in.interesses,
        nivel_educacional=user_in.nivel_educacional,
        habito_leitura=user_in.habito_leitura,
        role="aluno"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == login_data.email).first()
    if not user or not pwd_context.verify(_safe_password(login_data.password), user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "nome": user.nome,
        "email": user.email,
        "role": user.role
    }

@router.get("/me", response_model=UserResponse)
def get_me(current_user: Usuario = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserResponse)
def update_profile(user_update: UserUpdate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user
