import hashlib
from typing import Optional

from db_connection import get_connection
from modelos.usuario import Usuario


class UsuarioDAO:
    @staticmethod
    def hash_password(password: str) -> bytes:
        if password is None:
            return b""
        return hashlib.sha256(password.encode("utf-8")).digest()

    @staticmethod
    def autenticar(cedula: str, password: str) -> Optional[Usuario]:
        conn = get_connection()
        cursor = conn.cursor()
        password_hash = UsuarioDAO.hash_password(password)
        cursor.execute(
            """
            SELECT id_usuario, cedula, nombre, email, rol, estado, fecha_creacion, ultimo_acceso
            FROM Usuario
            WHERE cedula = ? AND password_hash = ? AND estado = 'Activo'
            """,
            (cedula, password_hash),
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return Usuario(
            id_usuario=row.id_usuario,
            cedula=row.cedula,
            nombre=row.nombre,
            email=row.email,
            rol=row.rol,
            estado=row.estado,
            fecha_creacion=row.fecha_creacion,
            ultimo_acceso=row.ultimo_acceso,
            password_hash=password_hash,
        )

    @staticmethod
    def actualizar_ultimo_acceso(id_usuario: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Usuario
            SET ultimo_acceso = SYSDATETIME()
            WHERE id_usuario = ?
            """,
            (id_usuario,),
        )
        conn.commit()
        conn.close()


    @staticmethod
    def listar() -> list[Usuario]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_usuario, cedula, nombre, email, rol, estado, fecha_creacion, ultimo_acceso
            FROM Usuario
            ORDER BY nombre
            """
        )
        rows = cursor.fetchall()
        conn.close()
        usuarios = []
        for row in rows:
            usuarios.append(
                Usuario(
                    id_usuario=row.id_usuario,
                    cedula=row.cedula,
                    nombre=row.nombre,
                    email=row.email,
                    rol=row.rol,
                    estado=row.estado,
                    fecha_creacion=row.fecha_creacion,
                    ultimo_acceso=row.ultimo_acceso,
                )
            )
        return usuarios


    @staticmethod
    def obtener_por_id(id_usuario: int) -> Optional[Usuario]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id_usuario, cedula, nombre, email, rol, estado, fecha_creacion, ultimo_acceso
            FROM Usuario
            WHERE id_usuario = ?
            """,
            (id_usuario,),
        )
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return Usuario(
            id_usuario=row.id_usuario,
            cedula=row.cedula,
            nombre=row.nombre,
            email=row.email,
            rol=row.rol,
            estado=row.estado,
            fecha_creacion=row.fecha_creacion,
            ultimo_acceso=row.ultimo_acceso,
        )

    @staticmethod
    def _existe_administrador(excluir_id: Optional[int] = None) -> bool:
        conn = get_connection()
        cursor = conn.cursor()
        if excluir_id is None:
            cursor.execute("SELECT COUNT(*) AS total FROM Usuario WHERE rol = 1")
        else:
            cursor.execute(
                "SELECT COUNT(*) AS total FROM Usuario WHERE rol = 1 AND id_usuario <> ?",
                (excluir_id,),
            )
        total = cursor.fetchone()[0]
        conn.close()
        return total > 0

    @staticmethod
    def crear(usuario: Usuario, password_claro: str) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        password_hash = UsuarioDAO.hash_password(password_claro)

        if usuario.rol == 1 and UsuarioDAO._existe_administrador():
            conn.close()
            raise ValueError("Ya existe un usuario administrador. Solo puede haber uno.")

        cursor.execute(
            """
            INSERT INTO Usuario (cedula, nombre, email, rol, estado, password_hash)
            OUTPUT INSERTED.id_usuario
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                usuario.cedula,
                usuario.nombre,
                usuario.email,
                usuario.rol,
                usuario.estado,
                password_hash,
            ),
        )
        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        return nuevo_id


    @staticmethod
    def actualizar(usuario: Usuario, password_claro: Optional[str] = None) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        existente = UsuarioDAO.obtener_por_id(usuario.id_usuario)
        if not existente:
            conn.close()
            raise ValueError("El usuario seleccionado ya no existe.")

        if usuario.rol == 1 and UsuarioDAO._existe_administrador(excluir_id=usuario.id_usuario):
            conn.close()
            raise ValueError("Ya existe otro administrador. Solo puede haber uno.")

        if existente.rol == 1 and usuario.rol != 1 and not UsuarioDAO._existe_administrador(excluir_id=usuario.id_usuario):
            conn.close()
            raise ValueError("Debe existir al menos un administrador en el sistema.")

        if password_claro:
            password_hash = UsuarioDAO.hash_password(password_claro)
            cursor.execute(
                """
                UPDATE Usuario
                SET cedula = ?, nombre = ?, email = ?, rol = ?, estado = ?, password_hash = ?
                WHERE id_usuario = ?
                """,
                (
                    usuario.cedula,
                    usuario.nombre,
                    usuario.email,
                    usuario.rol,
                    usuario.estado,
                    password_hash,
                    usuario.id_usuario,
                ),
            )
        else:
            cursor.execute(
                """
                UPDATE Usuario
                SET cedula = ?, nombre = ?, email = ?, rol = ?, estado = ?
                WHERE id_usuario = ?
                """,
                (
                    usuario.cedula,
                    usuario.nombre,
                    usuario.email,
                    usuario.rol,
                    usuario.estado,
                    usuario.id_usuario,
                ),
            )
        conn.commit()
        conn.close()


    @staticmethod
    def eliminar(id_usuario: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM Usuario WHERE id_usuario = ?",
            (id_usuario,),
        )
        conn.commit()
        conn.close()

