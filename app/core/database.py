#app/core/database.py
from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

"""
---CONEXIÓN REAL A LA BASE DE DATOS---
- Este archivo o módulo usa la config para abrir la conexión a PostgreSQL.
Este módulo se encarga de configurar la conexión a la base de datos PostgreSQL usando SQLModel.
- Crea el engine de SQLModel
- Crea sesiones para interactuar con la base de datos
- Dependencia para fastapi que provee una sesión por request (es decir, cada vez que se maneja una petición HTTP,
 se crea una sesión nueva y se cierra al finalizar la petición)
"""
# Crea el pool de conexiones a PostgreSQL (Es como decir: Conectate a PostgreSQL usando esta URL)
engine = create_engine(
    settings.DATABASE_URL, # Recibe la URL de conexión a la base de datos desde las variables de entorno
    echo=False # No muestra las consultas SQL en la consola (para no saturar el log)
)

# Crea las tablas automáticamente al iniciar la app (si no existen) en la base de datos según los modelos definidos
def create_db_and_tables() -> None:
    """Crea todas las tablas definidas con SQLModel al iniciar la app."""
    SQLModel.metadata.create_all(engine)

"""
Sesión por request:
Esto significa que cada request HTTP que necesite interactuar con la base de datos, 
va a recibir una sesión nueva y limpia.
Se abre -> se usa -> se cierra automáticamente al finalizar la petición (gracias al with).

"""
def get_session():
    """
    Dependencia FastAPI que provee una Session por request.
    Usada exclusivamente por el UnitOfWork — no inyectar directo en routers.
    """
    with Session(engine) as session:
        yield session # yield permite que esta función sea una dependencia de FastAPI 
        #que se puede usar con Depends() en los routers. Depends() se encarga de llamar a esta función, 
        # obtener la sesión y pasarla al UnitOfWork.
