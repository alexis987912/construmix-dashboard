import streamlit as st
import pandas as pd
import plotly.express as px
from auth_service import inicializar_sesion, iniciar_sesion, cerrar_sesion, USUARIOS_PRECONFIGURADOS
from data_engine import procesar_data_completa
from theme import aplicar_estilos_globales, COLOR_ROJO_PRIMARIO, COLOR_GRIS_OSCURO

st.set_page_config(
    page_title="CONSTRUMIX - Dashboard Analítico",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

inicializar_sesion()
aplicar_estilos_globales()

def mostrar_login():
    st.markdown("<h1 style='text-align: center;'>🏗️ CONSTRUMIX</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #666;'>Portal Gerencial de Proporciones y Significancia</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("---")
        with st.form("form_login"):
            correo = st.text_input("Correo Electrónico")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar")
            if submit:
                if iniciar_sesion(correo, password):
                    st.rerun()
                else:
                    st.error("Credenciales inválidas.")

def mostrar_dashboard():
    rol = st.session_state.rol_actual
    nombre_perfil = USUARIOS_PRECONFIGURADOS[st.session_state.usuario_actual]["nombre"]
    
    with st.sidebar:
        st.markdown(f"## {nombre_perfil}\n*(Rol: {rol.capitalize()})*")
        if st.button("Cerrar Sesión"):
            cerrar_sesion()
            st.rerun()
            
        st.write("---")
        st.markdown("### 📥 Ingesta Automática")
        archivo_subido = st.file_uploader("Reporte de Agregados (Excel)", type=["xlsx", "xls"])
        
    st.title("📊 Dashboard Gerencial de Operaciones")
    
    if not archivo_subido:
        st.info("Carga el archivo Excel de Remitos en la barra lateral para comenzar.")
        return
        
    try:
        df_base, df_materiales = procesar_data_completa(archivo_subido)
    except Exception as e:
        st.error(f"Error procesando la base de datos: {str(e)}")
        return
        
    if df_base.empty:
        st.error("El archivo cargado no contiene datos procesables en la hoja DATA.")
        return

    # --- FILTRO DE TEMPORALIDAD ---
    st.markdown("### 📅 Filtro de Temporalidad")
    tipo_filtro = st.radio("Selecciona el alcance del reporte:", ["Diario", "Mensual", "Anual"], horizontal=True)
    
    df_base_f = df_base.copy()
    df_mat_f = df_materiales.copy()
    
    if tipo_filtro == "Diario":
        fechas_disponibles = sorted(df_base['Fecha'].dt.date.unique())
        fecha_defecto = pd.to_datetime('2026-08-17').date()
        if fecha_defecto not in fechas_disponibles:
            fecha_defecto = fechas_disponibles[-1]
            
        fecha_sel = st.date_input("Día específico", value=fecha_defecto, min_value=fechas_disponibles[0], max_value=fechas_disponibles[-1])
        df_base_f = df_base_f[df_base_f['Fecha'].dt.date == fecha_sel]
        df_mat_f = df_mat_f[df_mat_f['Fecha'].dt.date == fecha_sel]
        titulo_fecha = f"del {fecha_sel.strftime('%d/%m/%Y')}"
        
    elif tipo_filtro == "Mensual":
        meses_disp = sorted(df_base['Fecha'].dt.to_period('M').unique())
        mes_defecto = meses_disp[-1]
        # Intenta buscar agosto 2026
        for m in meses_disp:
            if m.year == 2026 and m.month == 8:
                mes_defecto = m
                break
        mes_sel = st.selectbox("Mes específico", meses_disp, index=meses_disp.index(mes_defecto))
        df_base_f = df_base_f[df_base_f['Fecha'].dt.to_period('M') == mes_sel]
        df_mat_f = df_mat_f[df_mat_f['Fecha'].dt.to_period('M') == mes_sel]
        titulo_fecha = f"del mes {mes_sel}"
        
    elif tipo_filtro == "Anual":
        anios_disp = sorted(df_base['Fecha'].dt.year.unique())
        anio_defecto = 2026 if 2026 in anios_disp else anios_disp[-1]
        anio_sel = st.selectbox("Año específico", anios_disp, index=anios_disp.index(anio_defecto))
        df_base_f = df_base_f[df_base_f['Fecha'].dt.year == anio_sel]
        df_mat_f = df_mat_f[df_mat_f['Fecha'].dt.year == anio_sel]
        titulo_fecha = f"del año {anio_sel}"

    if df_base_f.empty:
        st.warning(f"No hay datos registrados para la selección.")
        return

    # --- 1. KPIs GLOBALES AVANZADOS ---
    st.markdown(f"### 📈 Indicadores Clave {titulo_fecha}")
    total_m3 = df_base_f['M3'].sum()
    total_teorico = df_mat_f['Consumo_Teorico'].sum()
    total_real = df_mat_f['Consumo_Real'].sum()
    diferencia_global = total_real - total_teorico
    porcentaje_desviacion = (diferencia_global / total_teorico * 100) if total_teorico > 0 else 0
    clientes_activos = df_base_f['Nombre cliente'].nunique()
    
    top_cliente = df_base_f.groupby('Nombre cliente')['M3'].sum().idxmax() if not df_base_f.empty else "N/A"
    top_formula = df_base_f.groupby('Fórmula')['M3'].sum().idxmax() if not df_base_f.empty else "N/A"
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Volumen Total Despachado", f"{total_m3:,.2f} M³")
    with col2:
        color_delta = "inverse" if porcentaje_desviacion > 0 else "normal"
        st.metric("Desviación Global de Insumos", f"{porcentaje_desviacion:,.2f} %", delta=f"{diferencia_global:,.2f} Und", delta_color=color_delta)
    with col3:
        st.metric("Cliente Principal (Top 1)", top_cliente)
    with col4:
        st.metric("Concreto Principal (Fórmula)", top_formula)

    st.write("---")
    
    # --- 1.5 EVOLUCIÓN EN EL TIEMPO (GRÁFICO APILADO) ---
    st.markdown("### 📊 Evolución del Volumen y Composición por Concreto")
    st.caption("Cálculo: Suma de Volumen (M³) distribuido en el tiempo, segmentado por las 5 Fórmulas más usadas (el resto se agrupa en 'Otras').")
    
    # Identify top 5 formulas to prevent color overflow
    top_5_formulas = df_base_f.groupby('Fórmula')['M3'].sum().nlargest(5).index.tolist()
    df_evolucion = df_base_f.copy()
    df_evolucion['Grupo_Fórmula'] = df_evolucion['Fórmula'].apply(lambda x: x if x in top_5_formulas else 'Otras')
    
    # Determinar el eje X según el filtro
    if tipo_filtro == "Anual":
        df_evolucion['Eje_X'] = df_evolucion['Fecha'].dt.strftime('%m - %b')
        x_label = "Meses"
    elif tipo_filtro == "Mensual":
        df_evolucion['Eje_X'] = df_evolucion['Fecha'].dt.strftime('%d - %a')
        x_label = "Días del Mes"
    else:
        # Diario
        df_evolucion['Eje_X'] = df_evolucion['Nombre cliente']
        x_label = "Clientes"
        
    df_evo_grouped = df_evolucion.groupby(['Eje_X', 'Grupo_Fórmula'])['M3'].sum().reset_index()
    
    fig_evo = px.bar(
        df_evo_grouped, 
        x='Eje_X', 
        y='M3', 
        color='Grupo_Fórmula',
        title="Distribución Total de Despachos",
        text=df_evo_grouped['M3'].apply(lambda x: f"{x:,.0f}" if x > 10 else ""),
        color_discrete_sequence=px.colors.sequential.Reds_r
    )
    fig_evo.update_layout(xaxis_title=x_label, yaxis_title="Volumen (M³)", barmode='stack')
    st.plotly_chart(fig_evo, use_container_width=True)
    
    st.write("---")

    # --- 2. TOP CLIENTES Y FÓRMULAS ---
    st.markdown("### 🏆 Ranking: Top 10 Clientes")
    
    # Top 10 Clientes
    df_clientes = df_base_f.groupby('Nombre cliente')['M3'].sum().reset_index()
    df_clientes = df_clientes.nlargest(10, 'M3').sort_values(by='M3', ascending=True)
    df_clientes['Participacion_%'] = (df_clientes['M3'] / total_m3) * 100
    
    fig_share = px.bar(
        df_clientes,
        y='Nombre cliente',
        x='M3',
        orientation='h',
        title="Top 10 Clientes por Volumen",
        text=df_clientes.apply(lambda row: f"{row['M3']:,.1f} M³ ({row['Participacion_%']:.1f}%)", axis=1),
        custom_data=['Participacion_%']
    )
    fig_share.update_traces(marker_color="#D91A1E", textposition='outside')
    fig_share.update_layout(yaxis_type='category', xaxis_title="Volumen (M³)")
    st.caption("Cálculo: Suma de M³ para los 10 clientes con mayor demanda respecto al Total del periodo.")
    st.plotly_chart(fig_share, use_container_width=True)
    
    st.write("---")
    st.markdown("### 🏆 Ranking: Top 10 Tipos de Concreto")
    # Top 10 Fórmulas
    df_formulas = df_base_f.groupby('Fórmula')['M3'].sum().reset_index()
    df_formulas = df_formulas.nlargest(10, 'M3').sort_values(by='M3', ascending=True)
    df_formulas['Participacion_%'] = (df_formulas['M3'] / total_m3) * 100
    
    fig_mix = px.bar(
        df_formulas,
        y='Fórmula',
        x='M3',
        orientation='h',
        title="Top 10 Tipos de Concreto",
        text=df_formulas.apply(lambda row: f"{row['M3']:,.1f} M³ ({row['Participacion_%']:.1f}%)", axis=1),
        custom_data=['Participacion_%']
    )
    fig_mix.update_traces(marker_color="#1E242B", textposition='outside')
    fig_mix.update_layout(yaxis_type='category', xaxis_title="Volumen (M³)")
    st.caption("Cálculo: Suma de M³ para los 10 concretos de mayor despacho respecto al Total del periodo.")
    st.plotly_chart(fig_mix, use_container_width=True)

    st.write("---")

    # --- 3. VARIACIONES EN DOSIFICACIONES POR FÓRMULA ---
    st.markdown("### 🔬 Variaciones en Dosificaciones por Fórmula")
    
    # Agrupar por fórmula
    df_form_var = df_mat_f.groupby('Formula')[['Consumo_Teorico', 'Consumo_Real']].sum().reset_index()
    df_form_var = df_form_var[df_form_var['Consumo_Teorico'] > 0] # Evitar divisiones por cero
    df_form_var['Diferencia'] = df_form_var['Consumo_Real'] - df_form_var['Consumo_Teorico']
    df_form_var['Variacion_%'] = (df_form_var['Diferencia'] / df_form_var['Consumo_Teorico']) * 100
    df_form_var = df_form_var.sort_values(by='Variacion_%', ascending=False)
    df_form_var['Color'] = df_form_var['Variacion_%'].apply(lambda x: COLOR_ROJO_PRIMARIO if x > 0 else "#28a745")

    fig_form = px.bar(
        df_form_var,
        x='Formula',
        y='Variacion_%',
        title="Desviación de Consumo (%) según Tipo de Concreto (Fórmula)",
        text=df_form_var['Variacion_%'].apply(lambda x: f"{x:.2f}%")
    )
    fig_form.update_traces(marker_color=df_form_var['Color'], textposition='outside')
    fig_form.update_layout(yaxis_title="Variación % (Positivo = Merma)", height=max(400, len(df_form_var) * 35))
    st.caption("Cálculo: ((Σ Consumo Real - Σ Consumo Teórico) / Σ Consumo Teórico) * 100 para cada Fórmula.")
    st.plotly_chart(fig_form, use_container_width=True)

    st.write("---")

    # --- 4. GRÁFICOS DE BARRAS (COMPOSICIÓN Y SIGNIFICANCIA) ---
    st.markdown("### 🏭 Composición Operativa y Desviaciones de Materiales")
    
    df_mat_agrupado = df_mat_f.groupby('Material')[['Consumo_Teorico', 'Consumo_Real']].sum().reset_index()
    df_mat_agrupado = df_mat_agrupado[df_mat_agrupado['Consumo_Teorico'] > 0]
    df_mat_agrupado['Diferencia'] = df_mat_agrupado['Consumo_Real'] - df_mat_agrupado['Consumo_Teorico']
    df_mat_agrupado['Variacion_%'] = (df_mat_agrupado['Diferencia'] / df_mat_agrupado['Consumo_Teorico']) * 100
    df_mat_agrupado['Color'] = df_mat_agrupado['Variacion_%'].apply(lambda x: COLOR_ROJO_PRIMARIO if x > 0 else "#28a745")
    
    fig_desv = px.bar(
        df_mat_agrupado,
        y='Material',
        x='Variacion_%',
        orientation='h',
        title="Desviación de Consumo por Material (%)",
        text=df_mat_agrupado['Variacion_%'].apply(lambda x: f"{x:.2f}%")
    )
    fig_desv.update_traces(marker_color=df_mat_agrupado['Color'], textposition='outside')
    fig_desv.update_layout(xaxis_title="Variación % (Positivo = Merma)", height=max(400, len(df_mat_agrupado) * 40))
    st.caption("Cálculo: ((Σ Real - Σ Teórico) / Σ Teórico) * 100 para cada Insumo.")
    st.plotly_chart(fig_desv, use_container_width=True)

    st.write("---")

    # --- 5. LOGÍSTICA Y DESEMPEÑO DE HORMIGONERAS ---
    st.markdown("### 🚚 Desempeño Operativo por Hormigonera (Mixers)")
    
    # Calcular Vueltas (viajes) y M3 totales por Mixer
    df_horm = df_base_f.groupby('Hormigonera').agg(
        M3=('M3', 'sum'),
        Vueltas=('M3', 'count')
    ).reset_index()
    
    # FORZAR A TEXTO CATEGÓRICO PARA EVITAR ESCALA NUMÉRICA LINEAL EN PLOTLY
    df_horm['Hormigonera'] = "Mixer " + df_horm['Hormigonera'].astype(str)
    
    df_horm['Participacion_%'] = (df_horm['M3'] / df_horm['M3'].sum()) * 100
    df_horm = df_horm.sort_values(by='M3', ascending=True)


    
    fig_operativa_m3 = px.bar(
        df_horm,
        y='Hormigonera',
        x='M3',
        orientation='h',
        title="Volumen Transportado por Mixer (M³)",
        text=df_horm['M3'].apply(lambda x: f"{x:.1f} M³")
    )
    fig_operativa_m3.update_traces(marker_color=COLOR_GRIS_OSCURO, textposition='outside')
    fig_operativa_m3.update_layout(yaxis_type='category', xaxis_title="M³", height=max(400, len(df_horm) * 35))
    st.caption("Cálculo: Suma aritmética de M³ despachados por Mixer.")
    st.plotly_chart(fig_operativa_m3, use_container_width=True)
    
    st.write("---")
    st.markdown("### 🚚 Desempeño Operativo: Vueltas por Mixer")
    df_horm_vueltas = df_horm.sort_values(by='Vueltas', ascending=True)
    fig_operativa_v = px.bar(
        df_horm_vueltas,
        y='Hormigonera',
        x='Vueltas',
        orientation='h',
        title="Cantidad de Viajes (Vueltas) por Mixer",
        text=df_horm_vueltas['Vueltas'].apply(lambda x: f"{x} vueltas")
    )
    fig_operativa_v.update_traces(marker_color=COLOR_ROJO_PRIMARIO, textposition='outside')
    fig_operativa_v.update_layout(yaxis_type='category', xaxis_title="Número de Vueltas", height=max(400, len(df_horm_vueltas) * 35))
    st.caption("Cálculo: Conteo de viajes/ciclos (vueltas) por Mixer.")
    st.plotly_chart(fig_operativa_v, use_container_width=True)

def main():
    if not st.session_state.autenticado:
        mostrar_login()
    else:
        mostrar_dashboard()

if __name__ == "__main__":
    main()
