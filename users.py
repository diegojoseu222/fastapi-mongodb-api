from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()

class User(BaseModel):
    id: int
    name: str
    email: str


users_db = [
    User(id=1, name="Alice", email="alice@example.com"),
    User(id=2, name="Bob", email="bob@example.com"),
    User(id=3, name="Charlie", email="charlie@example.com")
]


@router.get("/users")
async def get_users():
    return {"users": users_db}




@router.get("/users/search")
async def search_users(name: str = None, email: str = None):
    results = []
    for u in users_db:
        if name and name.lower() in u.name.lower():
            results.append(u)
        elif email and email == u.email:
            results.append(u)
        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontraron usuarios con los criterios proporcionados"
            )
    return {"users": results}



@router.get("/users/{user_id}")
async def get_user(user_id: int):
 # 1. Preparamos una variable vacía para guardar el resultado
    user_found = None
    
    # 2. Recorremos la lista uno por uno
    for u in users_db:
        if u.id == user_id:
            user_found = u
            break  # Lo encontramos, así que paramos el bucle
            
    # 3. Si al terminar el bucle sigue siendo None, lanzamos el error 404
    if user_found is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )       
    # 4. Si lo encontramos, lo devolvemos
    return user_found



class UserCreate(BaseModel):
    id: int
    name: str
    email: str

@router.post("/users")
async def create_user(user: UserCreate):
    # 1. Verificamos si el ID ya existe
    for u in users_db:
        if u.id == user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El ID del usuario ya existe"
            )
    
    # 2. Si no existe, lo agregamos a la base de datos simulada
    users_db.append(user)
    return {"message": "Usuario creado exitosamente", "user": user}


@router.put("/users/{user_id}")
async def update_user(user_id: int, user: UserCreate):
    for u in users_db:
        if u.id == user_id:
            u.name = user.name
            u.email = user.email
            return {"message": "Usuario actualizado exitosamente", "user": u}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado"
    )