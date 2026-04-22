#app/core/unit_of_work.py
from datetime import datetime, timezone
from sqlmodel import Session

"""
Unidad de Trabajo (Unit of Work) -> EL QUE DECIDE CUANDO HACER COMMIT(GUARDAR) O ROLLBACK(REVERTIR)
- Si todo salió bien → commit() → guarda los cambios en la base de datos.
- Si algo salió mal → rollback() → revierte cualquier cambio hecho durante la transacción.

- Patrón de diseño que agrupa operaciones relacionadas en una única transacción.
- Garantiza que todas las operaciones dentro de la unidad se completen exitosamente o se reviertan en caso de error.
- Facilita el manejo de transacciones y la coordinación entre múltiples repositorios.
- En este proyecto, el UnitOfWork se utiliza para inyectar la sesión de base de datos en los repositorios 
y controlar el ciclo de vida de las transacciones.

    Gestiona el ciclo de vida de la transacción de base de datos.

    Uso en servicios:
        with uow:
            uow.heroes.add(hero)
            uow.teams.add(team)
        # commit automático si no hay excepción
        # rollback automático si hay excepción

    El UoW es la única capa que llama a commit() y rollback().
    Los repositorios solo llaman a flush() para obtener IDs en memoria.
"""

class UnitOfWork:

    def __init__(self, session: Session) -> None:
        """
        Inicializa el UnitOfWork con una sesión activa de base de datos.

        Args:
            session (Session): Instancia de SQLModel/SQLAlchemy Session.
                               Representa el contexto de conexión y transacción.
        """
        self._session = session
        self.now = datetime.now(timezone.utc) #timestamp común para created_at, updated_at, deleted_at
    #------------------nuevo------------------------------------
    @property
    def session(self) -> Session:
        return self._session

    def __enter__(self) -> "UnitOfWork":
        """
        Método invocado al entrar en el contexto `with`.

        Returns:
            UnitOfWork: Retorna la propia instancia para operar dentro del bloque.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Método invocado al salir del contexto `with`.

        Controla automáticamente la transacción:
        - Si no hubo excepción → commit()
        - Si hubo excepción → rollback()

        Args:
            exc_type: Tipo de excepción (None si no hubo error)
            exc_val: Valor de la excepción
            exc_tb: Traceback de la excepción
        """
        if exc_type is None:
            self._session.commit()
        else:
            self._session.rollback()
        #Return false  ???????  ---------------------------------------------------------$%$#"#$$#"####""$$$$$###$$$##

    def commit(self) -> None:
        """
        Ejecuta un commit explícito de la transacción actual.
        """
        self._session.commit()

    def rollback(self) -> None:
        """
        Ejecuta un rollback explícito de la transacción actual.
        """
        self._session.rollback()