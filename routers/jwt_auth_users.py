from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Configuración JWT y Seguridad
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(
    prefix="/authJWT",
    tags=["authJWT"],
    responses={404: {"description": "Not found"}},
)

oauth2 = OAuth2PasswordBearer(tokenUrl="authJWT/login")
crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Modelos Pydantic
class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool


class UserDB(User):
    password: str


# Base de datos simulada con contraseñas hasheadas
users_db = {
    "alice": {
        "username": "alice",
        "full_name": "Alice Smith",
        "email": "alice@gmail.com",
        "disabled": False,
        "password": crypt.hash("secret1"),
    },
    "diego": {
        "username": "diego",
        "full_name": "Diego Rodriguez",
        "email": "diego@gmail.com",
        "disabled": True,
        "password": crypt.hash("secret2"),
    },
}


# Funciones auxiliares
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return crypt.verify(plain_password, hashed_password)


def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = search_user_db(username)
    if user is None:
        raise credentials_exception

    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo"
        )

    return user


# Endpoints
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_db = search_user_db(form_data.username)
    if not user_db or not verify_password(form_data.password, user_db.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario o contraseña incorrectos",
        )

    access_token = create_access_token(data={"sub": user_db.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=User)
async def me(user: User = Depends(get_current_user)):
    return user