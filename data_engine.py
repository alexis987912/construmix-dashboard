import pandas as pd
import streamlit as st
import numpy as np
from typing import Tuple

def parse_latin_number(val):
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        val = val.strip()
        if not val:
            return 0.0
        if '.' in val and ',' in val:
            if val.rfind(',') > val.rfind('.'):
                val = val.replace('.', '').replace(',', '.')
            else:
                val = val.replace(',', '')
        elif ',' in val:
            val = val.replace(',', '.')
        try:
            return float(val)
        except:
            return 0.0
    return 0.0

@st.cache_data(show_spinner="Procesando base de datos completa de operaciones...")
def procesar_data_completa(archivo_excel) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Lee la hoja DATA que contiene todos los despachos con la dosificación teórica y real.
    """
    df = pd.read_excel(archivo_excel, sheet_name="DATA")
    
    # Limpiar nombres de columnas principales
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df = df.dropna(subset=['Fecha', 'Fórmula', 'M3'])
    
    df['M3'] = df['M3'].apply(parse_latin_number)
    df['Hormigonera'] = df['Hormigonera'].astype(str).str.strip().str.replace('.0', '', regex=False)
    df['Fórmula'] = df['Fórmula'].astype(str).str.strip()
    df['Nombre cliente'] = df['Nombre cliente'].astype(str).str.strip()
    
    # Parse materials
    mat_cols = [
        ('Piedra', 'PI0001', 'PI00012'),
        ('Arena', 'AR0001', 'AR00013'),
        ('Cemento', 'CE0001', 'CE00014'),
        ('Huso', 'HS001', 'HS0015'),
        ('Agua', 'H2O', 'H2O6'),
        ('Aditivo_1', 'ADIT0004', 'ADIT00047'),
        ('Aditivo_2', 'ADIT0007', 'ADIT00078'),
        ('Aditivo_3', 'ADIT0008', 'ADIT00089'),
        ('Aditivo_4', 'ADIT0009', 'ADIT000910'),
        ('Aditivo_5', 'ADIT0010', 'ADIT001011'),
        ('Aditivo_6', 'ADIT0011', 'ADIT001112'),
        ('Aditivo_7', 'ADIT0012', 'ADIT001213'),
        ('Aditivo_8', 'ADIT0013', 'ADIT001314'),
        ('Aditivo_9', 'ADIT0014', 'ADIT001315')
    ]
    
    df_materiales_list = []
    
    for idx, row in df.iterrows():
        fecha = row['Fecha']
        formula = str(row['Fórmula']).strip()
        cliente = str(row['Nombre cliente']).strip()
        hormigonera = str(row['Hormigonera']).strip().replace('.0', '')
        m3 = row['M3']
        
        for mat_name, t_col, d_col in mat_cols:
            if t_col in df.columns and d_col in df.columns:
                t_val = parse_latin_number(row[t_col])
                d_val = parse_latin_number(row[d_col])
                
                if t_val > 0 or d_val > 0:
                    df_materiales_list.append({
                        "Fecha": fecha,
                        "Formula": formula,
                        "Hormigonera": hormigonera,
                        "Cliente": cliente,
                        "M3_Despachado": m3,
                        "Material": mat_name,
                        "Consumo_Teorico": t_val,
                        "Consumo_Real": d_val
                    })
                    
    df_materiales = pd.DataFrame(df_materiales_list)
    if not df_materiales.empty:
        df_materiales['Fecha'] = pd.to_datetime(df_materiales['Fecha'])
        df_materiales['Diferencia'] = df_materiales['Consumo_Real'] - df_materiales['Consumo_Teorico']
        df_materiales['Variacion_%'] = np.where(
            df_materiales['Consumo_Teorico'] > 0,
            (df_materiales['Diferencia'] / df_materiales['Consumo_Teorico']) * 100,
            0.0
        )
        
    return df, df_materiales
