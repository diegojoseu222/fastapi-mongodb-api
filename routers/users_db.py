# users db api 

from fastapi import APIRouter, HTTPException, status
from bson import ObjectId

# Importaciones locales de tu base de datos y esquemas
from db.client import db_client
from db.schemas.user import user_schema, users_schema
# Asume que tu modelo Pydantic de usuario está en db.models.user
from db.models.user import User

router = APIRouter(
    prefix="/userdb",
    tags=["userdb"],
    responses={status.HTTP_404_NOT_FOUND: {"message": "No encontrado"}}
)

# ---------------------------------------------------------
# FUNCIÓN AUXILIAR DE BÚSQUEDA EN MONGODB
# ---------------------------------------------------------
async def search_user(field: str, key):
    try:
        user = await db_client.users.find_one({field: key})
        if user:
            return User(**user_schema(user))
    except Exception:
        pass
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Usuario no encontrado"
    )

# ---------------------------------------------------------
# ENDPOINTS (CRUD)
# ---------------------------------------------------------

@router.get("/", response_model=list[User])
async def users():
    # Código para obtener todos los usuarios
   return users_schema(await db_client.users.find().to_list(100))
    

@router.get("/{id}", response_model=User)
async def user(id: str):
    # Código para buscar un usuario por id
    try:
        # 1. Buscamos directamente en Mongo convirtiendo el id (str) a ObjectId
        user = await db_client.users.find_one({"_id": ObjectId(id)})
    except Exception:
        # Si el id recibido no es un ObjectId válido de Mongo
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El id introducido no es válido"
        )
    # 2. Si no encuentra ningún usuario con ese id
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    # 3. Devolvemos el usuario parseado
    return User(**user_schema(user))



  # Código para crear un usuario
@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    
    found_user = await db_client.users.find_one({
        "$or": [
            {"email": user.email},
            {"username": user.username}
        ]
    })
    if found_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario o email ya existe"
        )

    user_dict = dict(user) # Convertir el modelo Pydantic a diccionario
    user_dict.pop("id", None) # Eliminar 'id' de forma segura

    # 1. Insertamos de forma asíncrona (con await) y guardamos el resultado
    inserted_user = await db_client.users.insert_one(user_dict)

    # 2. Buscamos el documento recién insertado por su _id generado por Mongo
    new_user = await db_client.users.find_one({"_id": inserted_user.inserted_id})

    # 3. Mapeamos con user_schema e instanciamos User
    return User(**user_schema(new_user))

 
@router.put("/", response_model=User)
async def update_user(user: User):
    # Código para actualizar un usuario
    user_dict = dict(user)
    user_dict.pop("id", None)  # Eliminar 'id' de forma segura

    try:
        updated_user = await db_client.users.find_one_and_replace(
            {"_id": ObjectId(user.id)},  # Filtramos por el id del usuario
            user_dict,                   # Reemplazamos con los nuevos datos
            return_document=True         # Devolvemos el documento actualizado
        )
    except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error al actualizar el usuario"
            )
    if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
    return User(**user_schema(updated_user))



@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: str):
    # Código para eliminar un usuario
    try:
        deleted_user = await db_client.users.find_one_and_delete({"_id": ObjectId(id)})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El id introducido no es válido"
        )
    if not deleted_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
 