import streamlit as st

# Diccionario estático de usuarios con sus respectivos roles y datos de perfil
USUARIOS_PRECONFIGURADOS = {
    "admin@construmix.pe": {
        "nombre": "Dirección General",
        "rol": "admin",
        "password": "admin"
    },
    "operaciones@construmix.pe": {
        "nombre": "Jefatura de Operaciones",
        "rol": "operaciones",
        "password": "oper"
    },
    "finanzas@construmix.pe": {
        "nombre": "Analítica Financiera",
        "rol": "finanzas",
        "password": "fina"
    }
}

def inicializar_sesion():
    """Inicializa las variables de estado de sesión relacionadas a la autenticación."""
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.usuario_actual = None
        st.session_state.rol_actual = None

def iniciar_sesion(correo: str, password: str) -> bool:
    """
    Verifica las credenciales del usuario.
    Devuelve True si el inicio de sesión es exitoso, False de lo contrario.
    """
    usuario = USUARIOS_PRECONFIGURADOS.get(correo)
    if usuario and usuario["password"] == password:
        st.session_state.autenticado = True
        st.session_state.usuario_actual = correo
        st.session_state.rol_actual = usuario["rol"]
        return True
    return False

def cerrar_sesion():
    """Limpia la sesión activa y devuelve al estado desautenticado."""
    st.session_state.autenticado = False
    st.session_state.usuario_actual = None
    st.session_state.rol_actual = None

def verificar_acceso_rol(roles_permitidos: list) -> bool:
    """
    Verifica si el rol del usuario actual está dentro de los roles permitidos.
    """
    if not st.session_state.autenticado:
        return False
    return st.session_state.rol_actual in roles_permitidos
