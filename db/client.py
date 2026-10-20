# Fichero para configurar la conexión asíncrona a la base de datos
from motor.motor_asyncio import AsyncIOMotorClient

# Creamos el cliente asíncrono apuntando a la base de datos 'local'
db_client = AsyncIOMotorClient("mongodb://localhost:27017").local