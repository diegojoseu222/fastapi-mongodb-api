from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import users_db

app = FastAPI(
    title="API de Usuarios con MongoDB",
    version="1.0.0"
)

# Montar recursos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir únicamente el router de MongoDB
app.include_router(users_db.router)


@app.get("/")
async def root():
    return {"message": "¡API con MongoDB funcionando correctamente!"}