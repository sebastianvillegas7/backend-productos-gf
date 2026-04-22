# Endpoints FastAPI del módulo Producto, usando el servicio para manejar la lógica de negocio
# app/modules/producto/router.py
from fastapi import APIRouter, Depends, Query, status
from typing import Annotated
from sqlmodel import Session

from app.core.database import get_session
from app.modules.producto.schema import ProductoCreate, ProductoRead, ProductoUpdate, ProductoList
from app.modules.producto.service import ProductoService

router = APIRouter(prefix="/productos", tags=["productos"])


def get_producto_service(session: Session = Depends(get_session)) -> ProductoService:
    """Factory de dependencia: inyecta el servicio con su Session."""
    return ProductoService(session)


# ── Endpoints ─────────────────────────────────────────────────────────────────

# CREATE
@router.post(
    "/",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un producto nuevo",
)
def create_producto(
    data: ProductoCreate,
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoRead:
    return svc.create(data)


# GET ALL
@router.get(
    "/",
    response_model=ProductoList,
    summary="Listar productos activos (paginado)",
)
def list_productos(
    offset: Annotated[int, Query(ge=0, description="Registros a omitir")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Máximo de registros")] = 20,
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoList:
    return svc.get_all_active(offset=offset, limit=limit)

# GET ALL Active + NO Active (Annotated + Query)
@router.get(
    "/all/",
    response_model=ProductoList,
    summary="Listar todos los productos",
)

def list_categorias_all(
    offset: Annotated[int, Query(ge=0, description="Cantidad de registros a omitir")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Cantidad máxima de registros")] = 20,
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoList:
    return svc.get_all(offset=offset, limit=limit)



# GET BY NOMBRE — debe ir ANTES de /{producto_id} para evitar que
# FastAPI interprete "buscar" como un entero y devuelva 422
@router.get(
    "/buscar/",
    response_model=ProductoRead,
    summary="Buscar producto por nombre",
)
def search_producto_by_nombre(
    nombre: str = Query(..., max_length=150, description="Nombre del producto a buscar"),
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoRead:
    return svc.get_by_nombre(nombre)


# GET BY ID
@router.get(
    "/{producto_id}",
    response_model=ProductoRead,
    summary="Obtener producto por ID",
)
def get_producto(
    producto_id: int,
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoRead:
    return svc.get_by_id(producto_id)


# UPDATE (PATCH)
@router.patch(
    "/{producto_id}",
    response_model=ProductoRead,
    summary="Actualización parcial de producto",
)
def update_producto(
    producto_id: int,
    data: ProductoUpdate,
    svc: ProductoService = Depends(get_producto_service),
) -> ProductoRead:
    return svc.update(producto_id, data)


# DELETE (soft delete)
@router.delete(
    "/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar producto (soft delete)",
)
def delete_producto(
    producto_id: int,
    svc: ProductoService = Depends(get_producto_service),
) -> None:
    svc.soft_delete(producto_id)