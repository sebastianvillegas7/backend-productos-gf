# Lógica de negocio y operaciones CRUD para Producto con la base de datos
from fastapi import HTTPException, status
from sqlmodel import Session
from app.modules.producto.schema import ProductoCreate, ProductoUpdate, ProductoRead, ProductoList
from app.modules.producto.model import Producto, ProductoCategoria, ProductoIngrediente
from app.modules.producto.unit_of_work import ProductoUnitOfWork

class ProductoService:

    def __init__(self, session: Session) -> None:
        self._session = session
    # ── Helpers privados ──────────────────────────────────────────────────────

    def _get_or_404(self, uow: ProductoUnitOfWork, producto_id: int) -> Producto:
        """
        Obtiene un ingrediente por ID o lanza excepción HTTP 404 si no existe.

        Args:
            uow (IngredienteUnitOfWork): Unidad de trabajo activa.
            ingrediente_id (int): ID de la categoría.

        Returns:
            Ingrediente: Instancia encontrada.

        Raises:
            HTTPException: 404 si la categoría no existe.

        """
        producto = uow.productos.get_by_id(producto_id)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con id={producto_id} no encontrado.",
            )
        return producto


    def _assert_nombre_unique(self, uow: ProductoUnitOfWork, nombre: str) -> None:
        """
        Valida que el nombre no esté en uso.

        Args:
            uow (IngredienteUnitOfWork): Unidad de trabajo activa.
            alias (str): Alias a validar.
        Raises:
            HTTPException: 409 si el nombre ya existe.
        Nota:
            Esta validación es a nivel aplicación, no reemplaza un UNIQUE en DB.
        """
        if uow.productos.get_by_nombre(nombre):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El nombre '{nombre}' ya está en uso.",
            )
        
    # ---------------------------------------------------REVISAR ----------------------$$%&%&$%$%$&$&$%$%$
    """
    def create(self, data: ProductoCreate) -> ProductoRead:
        with ProductoUnitOfWork(self._session) as uow:
            self._assert_nombre_unique(uow, data.nombre)

            producto = Producto(nombre=data.nombre, descripcion=data.descripcion, 
                                precio_base=data.precio_base, imagenes_url=data.imagenes_url, 
                                stock_cantidad=data.stock_cantidad, disponible=data.disponible
                                )
            
            if data.categoria_ids:
                categorias = []
                for categoria_id in data.categoria_ids:
                    categoria = uow.categorias.get_by_id(categoria_id)
                    if not categoria:
                        raise HTTPException(
                                    status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"La categoria con id='{categoria_id}' no encontrada.",
                            )
                    #---------------PREGUNTARR---------
                    if categoria.deleted_at is not None:
                        raise HTTPException(
                                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    detail="Hay una categoria que está dada de baja.",
                    )
                    categorias.append(categoria)
                producto.categorias = categorias

            if data.ingrediente_ids:
                ingredientes = []
                for ingrediente_id in data.ingrediente_ids:
                    ingrediente = uow.ingredientes.get_by_id(ingrediente_id)
                    if not ingrediente:
                        raise HTTPException(
                                    status_code=status.HTTP_404_not_found,
                                    detail=f"El ingrediente con id='{ingrediente_id}' no encontrada.",
                            )
                    # ------PREGUNTAR------
                    if ingrediente.deleted_at is not None:
                        raise HTTPException(
                                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                    detail="Hay un ingrediente dado de bajo.",
                            )
                    ingredientes.append(ingrediente)
                producto.ingredientes = ingredientes     
            
            uow.productos.add(producto)
            
            # Serializar dentro del contexto asegura acceso a atributos lazy
            result = ProductoRead.model_validate(producto)

        return result
    """

    
    def create(self, data: ProductoCreate) -> ProductoRead:
        with ProductoUnitOfWork(self._session) as uow:
        # 1. Validar nombre único
            self._assert_nombre_unique(uow, data.nombre)

        # 2. Crear producto base
            producto = Producto(
                nombre=data.nombre,
                descripcion=data.descripcion,
                precio_base=data.precio_base,
                imagenes_url=data.imagenes_url,
                stock_cantidad=data.stock_cantidad,
                disponible=data.disponible
            )
            
        # 5. Persistir
        #  ! CAMBIO: SQLAlchemy orden de persistencia de tablas intermedias.
            uow.productos.add(producto)

        # 3. Procesar categorías (tabla intermedia)
            # Validar que no haya categorías repetidas en la misma solicitud
            categoria_ids = [cat.categoria_id for cat in data.categorias]
            if len(categoria_ids) != len(set(categoria_ids)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se pueden repetir categorías en el mismo producto."
                )
            
            for cat in data.categorias:
                categoria = uow.categorias.get_by_id(cat.categoria_id)

                if not categoria:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Categoría con id={cat.categoria_id} no encontrada"
                    )

                if categoria.deleted_at is not None:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Hay una categoría dada de baja"
                    )

                producto_categoria = ProductoCategoria(
                    categoria=categoria,
                    es_principal=cat.es_principal
                )

                producto.categorias.append(producto_categoria)

        # 4. Procesar ingredientes (tabla intermedia)
            # Validar que no haya ingredientes repetidos en la misma solicitud
            ingrediente_ids = [ing.ingrediente_id for ing in data.ingredientes]
            if len(ingrediente_ids) != len(set(ingrediente_ids)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se pueden repetir ingredientes en el mismo producto."
                )
                
            for ing in data.ingredientes:
                ingrediente = uow.ingredientes.get_by_id(ing.ingrediente_id)

                if not ingrediente:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Ingrediente con id={ing.ingrediente_id} no encontrado"
                    )

                if ingrediente.deleted_at is not None:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Hay un ingrediente dado de baja"
                    )

                producto_ingrediente = ProductoIngrediente(
                    ingrediente=ingrediente,
                    es_removible=ing.es_removible
                )

                producto.ingredientes.append(producto_ingrediente)


        # 6. Serializar
            result = ProductoRead.model_validate(producto)

        return result

        
    # REVISAR ----------------
    def get_all_active(self, offset: int = 0, limit: int = 20) -> ProductoList:
        """
        Obtiene lista paginada de héroes activos.

        Args:
            offset (int): Desplazamiento.
            limit (int): Límite de resultados.

        Returns:
            CategoriaList: DTO con lista de categorías y total.

        Nota:
            El total se calcula con una query separada.
        """
        with ProductoUnitOfWork(self._session) as uow:
            productos = uow.productos.get_active(offset=offset, limit=limit)
            total = uow.productos.count()

            result = ProductoList(
                data=[ProductoRead.model_validate(c) for c in productos],
                total=total,
            )

        return result
    
    # TO DO (REVISAR)-----
    def get_all(self, offset: int = 0, limit: int = 20) -> ProductoList:
        """
        Obtiene lista paginada de todos los ingredientes.

        Args:
            offset (int): Desplazamiento.
            limit (int): Límite de resultados.

        Returns:
            ProductoList: DTO con lista de categorías y total.

        Nota:
            El total se calcula con una query separada.
        """
        with ProductoUnitOfWork(self._session) as uow:
            productos = uow.productos.get_all(offset=offset, limit=limit)
            total = len(productos)

            result = ProductoList(
                data=[ProductoRead.model_validate(c) for c in productos],
                total=total,
            )

        return result
    
    # REVISAR------------------------------
    def get_by_id(self, producto_id: int) -> ProductoRead:
        """
        Obtiene un producto por ID.

        Args:
            producto_id (int): ID del producto.

        Returns:
            ProductoRead: DTO del producto.

        Raises:
            HTTPException: 404 si no existe.
        """
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            result = ProductoRead.model_validate(producto)

        return result
    """
    # Revisar----------------VIEJOOOOO MÉTODOOOO (ABAJO ESTÁ EL QUE SE USA)----------------------------
    def update(self, producto_id: int, data: ProductoUpdate) -> ProductoRead:
    
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)

            if data.nombre and data.nombre != producto.nombre:
                self._assert_nombre_unique(uow, data.nombre)

            # Solo campos enviados por el cliente
            # patch = data.model_dump(exclude_unset=True)  ------------------------ CAAAMBIO AQUÍ-----------------
            patch = data.model_dump(exclude_unset=True, exclude={"categorias", "ingredientes"})
            # ANTES:
            # Solo campos enviados por el cliente
            #patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(producto, field, value)

            producto.updated_at = uow.now
            uow.productos.add(producto)
            result = ProductoRead.model_validate(producto)

        return result
    """

        # Revisar-----------------------------------
    def update(self, producto_id: int, data: ProductoUpdate) -> ProductoRead:
    
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)

            if data.nombre and data.nombre != producto.nombre:
                self._assert_nombre_unique(uow, data.nombre)

            # Solo campos enviados por el cliente
            # patch = data.model_dump(exclude_unset=True)  ------------------------ CAAAMBIO AQUÍ-----------------
            patch = data.model_dump(exclude_unset=True, exclude={"categorias", "ingredientes"})
            # ANTES:
            # Solo campos enviados por el cliente
            #patch = data.model_dump(exclude_unset=True)
            for field, value in patch.items():
                setattr(producto, field, value)
            
            # No permite dejar sin categorías o ingredientes
            if data.categorias is not None and len(data.categorias) == 0:
                raise HTTPException(400, "Debe tener al menos una categoría")

            if data.ingredientes is not None and len(data.ingredientes) == 0:
                raise HTTPException(400, "Debe tener al menos un ingrediente")
            
            # Categorías — None = no tocar, [] = borrar todas, [items] = reemplazar            
                # Validar que no haya categorías repetidas en la misma solicitud
            if data.categorias is not None:
                categoria_ids = [cat.categoria_id for cat in data.categorias]
                if len(categoria_ids) != len(set(categoria_ids)):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No se pueden repetir categorías en el mismo producto."
                    )
                                        
            if data.categorias is not None:
                for pc in list(producto.categorias):   # list() para iterar copia segura mientras se modifica
                    uow.session.delete(pc)
                uow.session.flush()   

                for cat in data.categorias:
                    categoria = uow.categorias.get_by_id(cat.categoria_id)
                    if not categoria:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Categoría con id={cat.categoria_id} no encontrada"
                        )
                    if categoria.deleted_at is not None:
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"La categoría con id={cat.categoria_id} está dada de baja"
                        )
                    producto.categorias.append(
                        ProductoCategoria(
                            producto=producto,
                            categoria=categoria,
                            es_principal=cat.es_principal
                        )
                    )

        # Ingredientes — None = no tocar, [] = borrar todos, [items] = reemplazar
            # Validar que no haya ingredientes repetidos en la misma solicitud
            if data.ingredientes is not None:
                ingrediente_ids = [ing.ingrediente_id for ing in data.ingredientes]
                if len(ingrediente_ids) != len(set(ingrediente_ids)):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No se pueden repetir ingredientes en el mismo producto."
                    )
        
            if data.ingredientes is not None:
                for pi in list(producto.ingredientes):
                    uow.session.delete(pi)
                uow.session.flush()

                for ing in data.ingredientes:
                    ingrediente = uow.ingredientes.get_by_id(ing.ingrediente_id)
                    if not ingrediente:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Ingrediente con id={ing.ingrediente_id} no encontrado"
                        )
                    if ingrediente.deleted_at is not None:
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"El ingrediente con id={ing.ingrediente_id} está dado de baja"
                        )
                    producto.ingredientes.append(
                        ProductoIngrediente(
                            producto=producto,
                            ingrediente=ingrediente,
                            es_removible=ing.es_removible
                        )
                    )
                    
            producto.updated_at = uow.now            
            result = ProductoRead.model_validate(producto)

        return result

    def  get_by_nombre(self, nombre: str) -> ProductoRead:
        """
        Busca una categoría por su nombre.

        Args:
            nombre (str): Nombre de la categoría a buscar.

        Returns:
            CategoriaRead: DTO de la categoría encontrada.

        Raises:
            HTTPException: 404 si no se encuentra una categoría con el nombre dado.
        """
        with ProductoUnitOfWork(self._session) as uow:
            producto = uow.productos.get_by_nombre(nombre)
            if not producto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto con nombre='{nombre}' no encontrado",
                )
            result = ProductoRead.model_validate(producto)

        return result
    
    # ------------------------------------REVISAR ------------------
    def soft_delete(self, producto_id: int) -> None:
        """
        Realiza un borrado lógico de la categoría.

        Flujo:
        - Obtiene entidad
        - Marca como inactivo
        - Persiste cambio

        Args:
            producto_id (int): ID de la categoría.

        Nota:
            No elimina físicamente el registro de la base de datos.
        """
        with ProductoUnitOfWork(self._session) as uow:
            producto = self._get_or_404(uow, producto_id)
            """
            -----------------REVISAAAAAAAR PARA PRODUCTO: -------------------------------------
            if ingrediente.productos:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No se puede eliminar un ingrediente asociado a uno o más productos."
                )
            """
            producto.deleted_at = uow.now
            producto.updated_at = uow.now
            uow.productos.add(producto)