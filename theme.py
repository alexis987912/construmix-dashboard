import streamlit as st

# Paleta de colores de CONSTRUMIX
COLOR_ROJO_PRIMARIO = "#D91A1E"
COLOR_ROJO_ACENTO = "#C4161A"
COLOR_GRIS_OSCURO = "#1E242B"
COLOR_SUPERFICIE = "#F4F6F9"
COLOR_BORDES = "#E2E8F0"

def aplicar_estilos_globales():
    """
    Inyecta código CSS global para personalizar el aspecto de la aplicación
    según la identidad corporativa de CONSTRUMIX.
    """
    estilo_css = f"""
    <style>
        /* Color de fondo principal */
        .stApp {{
            background-color: {COLOR_SUPERFICIE};
            color: {COLOR_GRIS_OSCURO};
        }}
        
        /* Botones primarios */
        .stButton>button {{
            background-color: {COLOR_ROJO_PRIMARIO};
            color: white;
            border-radius: 4px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }}
        .stButton>button:hover {{
            background-color: {COLOR_ROJO_ACENTO};
            color: white;
            border: none;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {COLOR_GRIS_OSCURO};
        }}
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}
        
        /* Tarjetas de Métricas (KPIs) */
        div[data-testid="stMetricValue"] {{
            color: {COLOR_ROJO_PRIMARIO};
            font-size: 2rem;
            font-weight: bold;
        }}
        div[data-testid="metric-container"] {{
            background-color: white;
            border: 1px solid {COLOR_BORDES};
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        /* Títulos */
        h1, h2, h3 {{
            color: {COLOR_GRIS_OSCURO} !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        /* Estilos del Chatbot Agresivos para sobrescribir el Modo Oscuro nativo */
        div[data-testid="stChatMessage"], .stChatMessage {{
            background-color: white !important;
            border: 1px solid {COLOR_BORDES} !important;
            border-radius: 8px !important;
            padding: 1rem !important;
        }}
        div[data-testid="stChatMessage"] *, .stChatMessage * {{
            color: {COLOR_GRIS_OSCURO} !important;
        }}
        div[data-testid="stMarkdownContainer"] p {{
            color: {COLOR_GRIS_OSCURO} !important;
        }}
        
        /* Ocultar menú de Streamlit y footer */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
    </style>
    """
    st.markdown(estilo_css, unsafe_allow_html=True)
