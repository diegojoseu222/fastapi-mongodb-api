from fastapi import FastAPI
from users import router as users_router

app = FastAPI()
app.include_router(users_router)

@app.get("/")
async def root():
    return {"message": "¡API funcionando correctamente!"}

@app.get("/saludo")
async def saludo():
    return {"message": "¡Hola! Bienvenido a la API."}