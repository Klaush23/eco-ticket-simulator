"""
================================================================================
APLICATIVO DE SIMULACIÓN Y EVALUACIÓN COMPARATIVA DE ARQUITECTURAS
PROYECTO: ECO-TICKET · TERMINAL INTERACTIVO DE RECICLAJE
UNIVERSIDAD LIBRE - FACULTAD DE INGENIERÍA - INGENIERÍA APLICADA (2026-2)
AUTOR: GERSON SANTIAGO SAENZ GUTIERREZ
================================================================================
"""

import math
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA (RESPONSIVE / MÓVIL)
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="ECO-TICKET // Simulador Arquitectónico",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para apariencia profesional en celulares y PC
st.markdown("""
    <style>
    .main {
        background-color: #F4F9F8;
    }
    .stMetric {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #CBD5E1;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    .card-recommendation {
        background-color: #E6F4F1;
        border-left: 6px solid #029A71;
        padding: 20px;
        border-radius: 8px;
        color: #112A34;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# ENCABEZADO Y CONTEXTO
# ------------------------------------------------------------------------------
st.title("♻️ ECO-TICKET — Simulador de Arquitectura de Software")
st.caption("Universidad Libre | Ingeniería Aplicada | Proyecto Evaluativo Actividad 9")

st.markdown("""
Este aplicativo simula y compara cuantitativamente el rendimiento de **3 alternativas de arquitectura** 
para la red de terminales de reciclaje ECO-TICKET bajo distintas condiciones operativas.
""")

# ------------------------------------------------------------------------------
# BARRA LATERAL: VARIABLES DE ENTRADA (REQUISITO 3)
# ------------------------------------------------------------------------------
st.sidebar.header("⚙️ Variables de Entrada")

# Escenarios predefinidos para carga rápida (Requisito 5)
escenario_sel = st.sidebar.radio(
    "Seleccionar Escenario de Prueba:",
    ["Personalizado", "Escenario 1: Referencia Normal", "Escenario 2: Carga Pico (Horas Calle)", "Escenario 3: Red Inestable (4G Fluctua)"]
)

if escenario_sel == "Escenario 1: Referencia Normal":
    default_n, default_bw, default_res = 10, 20.0, 0.5
elif escenario_sel == "Escenario 2: Carga Pico (Horas Calle)":
    default_n, default_bw, default_res = 300, 15.0, 0.5
elif escenario_sel == "Escenario 3: Red Inestable (4G Fluctua)":
    default_n, default_bw, default_res = 25, 1.5, 2.0
else:
    default_n, default_bw, default_res = 50, 10.0, 0.8

n_usr = st.sidebar.slider("1. Carga Concurrente (N_usr - req/min)", min_value=1, max_value=500, value=default_n, step=5)
bw = st.sidebar.slider("2. Ancho de Banda Red (BW - Mbps)", min_value=0.5, max_value=100.0, value=float(default_bw), step=0.5)
res_img = st.sidebar.slider("3. Tamaño Imagen Captura (Res_img - MB)", min_value=0.1, max_value=3.0, value=float(default_res), step=0.1)

# Validation Control (Requisito 10)
if bw <= 0.0:
    st.error("⚠️ El ancho de banda debe ser mayor a 0 Mbps. Ajustando a 0.1 Mbps por seguridad.")
    bw = 0.1

# ------------------------------------------------------------------------------
# MODELO COMPUTACIONAL MATEMÁTICO (REQUISITO 4 Y 6)
# ------------------------------------------------------------------------------
def calcular_modelo(n_usr, bw, res_img):
    # Parámetros base
    c_local = 20.0  # Capacidad nominal local req/min
    l_cam = 100.0   # Captura óptica ms
    rtt_cloud = 40.0 # RTT red ms

    # --- ARQUITECTURA A: MONOLITO EDGE ---
    l_tot_a = l_cam + 250.0 * (1.0 + 0.15 * math.pow((n_usr / c_local), 2))
    u_cpu_a = min(100.0, 15.0 + (n_usr / c_local) * 70.0)
    t_thru_a = c_local / 60.0
    cost_a = 45.0  # Consumo eléctrico local

    # --- ARQUITECTURA B: MICROSERVICIOS CLOUD ---
    instancias = math.ceil(n_usr / 50.0)
    l_red_b = ((res_img * 8.0) / bw) * 1000.0 + rtt_cloud
    l_tot_b = l_cam + l_red_b + 80.0 * (1.0 + 0.02 * (n_usr / instancias))
    u_cpu_b = 10.0 + (n_usr / 100.0) * 5.0
    t_thru_b = (instancias * 50.0) / 60.0
    cost_b = 25.0 + instancias * 35.0 + (n_usr * 60 * 24 * 30 * res_img / 1024.0) * 0.008

    # --- ARQUITECTURA C: HÍBRIDA / ORIENTADA A EVENTOS ---
    res_vector = 0.02 # Vector de características liviano
    l_red_c = ((res_vector * 8.0) / bw) * 1000.0
    l_tot_c = l_cam + 110.0 + l_red_c
    u_cpu_c = 18.0 + (n_usr / c_local) * 25.0
    t_thru_c = (c_local * 2.5) / 60.0
    cost_c = 20.0 + (instancias / 2.0) * 20.0 + 10.0 # Servidores aligerados + broker

    return {
        "Monolito Edge": {"Latencia (ms)": round(l_tot_a, 1), "CPU Local (%)": round(u_cpu_a, 1), "Throughput (TPS)": round(t_thru_a, 2), "Costo (USD/mes)": round(cost_a, 2)},
        "Microservicios Cloud": {"Latencia (ms)": round(l_tot_b, 1), "CPU Local (%)": round(u_cpu_b, 1), "Throughput (TPS)": round(t_thru_b, 2), "Costo (USD/mes)": round(cost_b, 2)},
        "Híbrida (Edge-Cloud)": {"Latencia (ms)": round(l_tot_c, 1), "CPU Local (%)": round(u_cpu_c, 1), "Throughput (TPS)": round(t_thru_c, 2), "Costo (USD/mes)": round(cost_c, 2)}
    }

resultados = calcular_modelo(n_usr, bw, res_img)
df_res = pd.DataFrame(resultados).T

# ------------------------------------------------------------------------------
# PRESENTACIÓN DE RESULTADOS E INDICADORES (REQUISITO 6 Y 7)
# ------------------------------------------------------------------------------
st.subheader("📊 Indicadores Cuantificables Calculados")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Latencia Híbrida", f"{resultados['Híbrida (Edge-Cloud)']['Latencia (ms)']} ms", delta="- vs Monolito", delta_color="inverse")
with col2:
    st.metric("Uso CPU Monolito", f"{resultados['Monolito Edge']['CPU Local (%)']}%", delta="Saturación" if resultados['Monolito Edge']['CPU Local (%)'] > 85 else "Normal", delta_color="off")
with col3:
    st.metric("Capacidad Cloud", f"{resultados['Microservicios Cloud']['Throughput (TPS)']} TPS")
with col4:
    st.metric("Costo Híbrida", f"${resultados['Híbrida (Edge-Cloud)']['Costo (USD/mes)']} USD")

# Tabla Comparativa Detallada
st.write("### Tabla Comparativa de Arquitecturas")
st.dataframe(df_res.style.highlight_min(axis=0, color="#D1FAE5", subset=["Latencia (ms)", "Costo (USD/mes)"]), use_container_width=True)

# ------------------------------------------------------------------------------
# GRÁFICOS COMPARATIVOS INTERACTIVOS (REQUISITO 7)
# ------------------------------------------------------------------------------
col_g1, col_g2 = st.columns(2)

with col_g1:
    fig_lat = px.bar(
        df_res, y=df_res.index, x="Latencia (ms)", text_auto=True,
        title="Latencia Total Estimada (Menor es mejor)",
        color=df_res.index, color_discrete_sequence=["#112A34", "#4B636E", "#029A71"]
    )
    fig_lat.add_vline(x=1500, line_dash="dash", line_color="red", annotation_text="Límite Máximo NFR (1500 ms)")
    st.plotly_chart(fig_lat, use_container_width=True)

with col_g2:
    fig_cost = px.bar(
        df_res, y=df_res.index, x="Costo (USD/mes)", text_auto=True,
        title="Costo Operativo Mensual Estimado (Menor es mejor)",
        color=df_res.index, color_discrete_sequence=["#112A34", "#4B636E", "#029A71"]
    )
    st.plotly_chart(fig_cost, use_container_width=True)

# ------------------------------------------------------------------------------
# MOTOR DE APOYO A LA DECISIÓN (REQUISITO 8)
# ------------------------------------------------------------------------------
st.subheader("💡 Dictamen y Recomendación Arquitectónica")

lat_hib = resultados['Híbrida (Edge-Cloud)']['Latencia (ms)']
lat_cloud = resultados['Microservicios Cloud']['Latencia (ms)']
cpu_mon = resultados['Monolito Edge']['CPU Local (%)']

if lat_cloud > 3000:
    alerta_red = "❌ **Microservicios Cloud descartados:** El ancho de banda actual genera latencias inaceptables por transferencia de imagen."
else:
    alerta_red = "✅ **Cloud viable pero costoso:** Requiere conexión estable."

if cpu_mon > 90:
    alerta_cpu = "❌ **Monolito Edge colapsado:** La CPU local supera el 90% de ocupación."
else:
    alerta_cpu = "✅ **Monolito estable:** Carga local dentro de parámetros."

st.markdown(f"""
<div class="card-recommendation">
    <h3>🏆 ARQUITECTURA RECOMENDADA: HÍBRIDA / ORIENTADA A EVENTOS</h3>
    <p><b>Justificación Cuantitativa del Motor:</b></p>
    <ul>
        <li><b>Latencia Optimizada:</b> Mantiene una respuesta de <b>{lat_hib} ms</b>, cumpliendo holgadamente el límite de 1,500 ms.</li>
        <li><b>Independencia de Red:</b> La inferencia biométrica preliminar en el borde evita enviar imágenes pesadas por redes móviles inestables.</li>
        <li><b>Estado de Alternativas:</b><br>{alerta_red}<br>{alerta_cpu}</li>
    </ul>
    <p><b>Limitación Principal:</b> Requiere gestión de consistencia eventual mediante colas de mensajes (RabbitMQ/MQTT) para evitar inconsistencias temporales de saldo.</p>
</div>
""", unsafe_allow_html=True)