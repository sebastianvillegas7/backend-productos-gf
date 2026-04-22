# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import create_db_and_tables
from app.modules.categoria.router import router as categoria_router
from app.modules.ingrediente.router import router as ingrediente_router
from app.modules.producto.router import router as producto_router
from fastapi.middleware.cors import CORSMiddleware
"""
---ES EL PUNTO DE ENTRADA DE LA APLICACIÓN---
- Aquí se crea la instancia de FastAPI, se configura el lifespan (ciclo de vida) de la aplicación, 
y se incluyen los routers.
"""

@asynccontextmanager # Su funcion es definir el ciclo de vida de la aplicación, 
# en este caso, para crear las tablas al iniciar la app
async def lifespan(app: FastAPI):
    create_db_and_tables() # Llamamos a la función que crea las tablas en la base de datos al iniciar la app
    yield # Aquí se ejecuta el código de la app (routers, etc)
    
app = FastAPI(
    title="API Parcial", 
    description="API para el parcial de programación backend", 
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categoria_router)
app.include_router(ingrediente_router)
app.include_router(producto_router)
