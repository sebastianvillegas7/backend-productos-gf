# app/modules/ingrediente/router.py
from fastapi import APIRouter, Depends, Query, status
from typing import Annotated
from sqlmodel import Session

from app.core.database import get_session
from app.modules.ingrediente.schema import IngredienteCreate, IngredienteRead, IngredienteUpdate, IngredienteList
from app.modules.ingrediente.service import IngredienteService

router = APIRouter(prefix="/ingredientes", tags=["ingredientes"])

# Esto lo que hace es crear una función que se puede usar como dependencia en los endpoints, 
# y que se encargará de crear una instancia del servicio con la sesión de base de datos inyectada.
def get_ingrediente_service(session: Session = Depends(get_session)) -> IngredienteService:
    """Factory de dependencia: inyecta el servicio con su Session."""
    return IngredienteService(session)

# ── Endpoints ─────────────────────────────────────────────────────────────────

# CREATE
@router.post(
    "/",
    response_model=IngredienteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un ingrediente nuevo",
)
def create_ingrediente(
    data: IngredienteCreate,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredienteRead:
    """Router delega al servicio — sin lógica de negocio aquí."""
    return svc.create(data)


# GET ALL (Annotated + Query)
@router.get(
    "/",
    response_model=IngredienteList,
    summary="Listar ingredientes activos (paginado)",
)
def list_ingredientes(
    offset: Annotated[int, Query(ge=0, description="Cantidad de registros a omitir")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Cantidad máxima de registros")] = 20,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredienteList:
    return svc.get_all_active(offset=offset, limit=limit)


# GET ALL Active + NO Active (Annotated + Query)
@router.get(
    "/all/",
    response_model=IngredienteList,
    summary="Listar todos los ingredientes",
)

def list_ingredientes_all(
    offset: Annotated[int, Query(ge=0, description="Cantidad de registros a omitir")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Cantidad máxima de registros")] = 20,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredienteList:
    return svc.get_all(offset=offset, limit=limit)


# GET por nombre
@router.get(
    "/buscar/",
    response_model=IngredienteRead,
    summary="Buscar ingrediente por nombre",
)
def search_ingrediente_by_nombre(
    nombre: str = Query(..., max_length=100, description="Nombre del ingrediente a buscar"),
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredienteRead:
    return svc.get_by_nombre(nombre)


# GET ALL alergenos
@router.get(
    "/alergenos/",
    response_model=IngredienteList,
    summary="Listar ingredientes activos (paginado)",
)
def list_alergenos(
    offset: Annotated[int, Query(ge=0, description="Cantidad de registros a omitir")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Cantidad máxima de registros")] = 20,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredienteList:
    return svc.get_alergenos(offset=offset, limit=limit)


# GET BY ID
@router.get(
    "/{ingrediente_id}",
    response_model=IngredienteRead,
    summary="Obtener ingrediente por ID",
)
def get_ingrediente(
    ingrediente_id: int,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredienteRead:
    return svc.get_by_id(ingrediente_id)



# UPDATE (PATCH) 
@router.patch(
    "/{ingrediente_id}",
    response_model=IngredienteRead,
    summary="Actualización parcial de ingrediente",
)
def update_ingrediente(
    ingrediente_id: int,
    data: IngredienteUpdate,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> IngredienteRead:
    return svc.update(ingrediente_id, data)



# DELETE (soft delete)
@router.delete(
    "/{ingrediente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar ingrediente (soft delete)",
)
def delete_ingrediente(
    ingrediente_id: int,
    svc: IngredienteService = Depends(get_ingrediente_service),
) -> None:
    svc.soft_delete(ingrediente_id)
