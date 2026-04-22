# app/modules/categoria/router.py
from fastapi import APIRouter, Depends, Query, status
from typing import Annotated
from sqlmodel import Session

from app.core.database import get_session
from app.modules.categoria.schema import CategoriaCreate, CategoriaRead, CategoriaUpdate, CategoriaList
from app.modules.categoria.service import CategoriaService

router = APIRouter(prefix="/categorias", tags=["categorias"])

# Esto lo que hace es crear una función que se puede usar como dependencia en los endpoints, 
# y que se encargará de crear una instancia del servicio con la sesión de base de datos inyectada.
def get_categoria_service(session: Session = Depends(get_session)) -> CategoriaService:
    """Factory de dependencia: inyecta el servicio con su Session."""
    return CategoriaService(session)

# ── Endpoints ─────────────────────────────────────────────────────────────────

# CREATE
@router.post(
    "/",
    response_model=CategoriaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una categoría nueva",
)
def create_categoria(
    data: CategoriaCreate,
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaRead:
    """Router delega al servicio — sin lógica de negocio aquí."""
    return svc.create(data)

# GET ALL Active (Annotated + Query)
@router.get(
    "/",
    response_model=CategoriaList,
    summary="Listar categorías activas (paginado)",
)
def list_categorias(
    offset: Annotated[int, Query(ge=0, description="Cantidad de registros a omitir")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Cantidad máxima de registros")] = 20,
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaList:
    return svc.get_all_active(offset=offset, limit=limit)

# GET ALL Active + NO Active (Annotated + Query)
@router.get(
    "/all/",
    response_model=CategoriaList,
    summary="Listar todas las categorias",
)

def list_categorias_all(
    offset: Annotated[int, Query(ge=0, description="Cantidad de registros a omitir")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Cantidad máxima de registros")] = 20,
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaList:
    return svc.get_all(offset=offset, limit=limit)


# GET por nombre
@router.get(
    "/buscar/",
    response_model=CategoriaRead,
    summary="Buscar categoría por nombre",
)
def search_categoria_by_nombre(
    nombre: str = Query(..., max_length=100, description="Nombre de la categoría a buscar"),
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaRead:
    return svc.get_by_nombre(nombre)


# GET BY ID
@router.get(
    "/{categoria_id}",
    response_model=CategoriaRead,
    summary="Obtener categoría por ID",
)
def get_categoria(
    categoria_id: int,
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaRead:
    return svc.get_by_id(categoria_id)


# UPDATE (PATCH) 
@router.patch(
    "/{categoria_id}",
    response_model=CategoriaRead,
    summary="Actualización parcial de categoría",
)
def update_categoria(
    categoria_id: int,
    data: CategoriaUpdate,
    svc: CategoriaService = Depends(get_categoria_service),
) -> CategoriaRead:
    return svc.update(categoria_id, data)


# DELETE (soft delete)
@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar categoría (soft delete)",
)
def delete_categoria(
    categoria_id: int,
    svc: CategoriaService = Depends(get_categoria_service),
) -> None:
    svc.soft_delete(categoria_id)
