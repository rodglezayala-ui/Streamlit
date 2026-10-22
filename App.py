
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar la página de Streamlit
st.set_page_config(
    page_title="Dashboard de Análisis de Ventas y Pérdidas",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ruta del archivo
FILE_PATH = 'SalidaVentas.xlsx'

@st.cache_data
def load_data():
    df = pd.read_excel(FILE_PATH)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"No se pudo cargar el archivo en {FILE_PATH}. Asegúrate de que la ruta sea correcta.")
    st.stop()

# Título del Dashboard
st.title("📊 Dashboard Interactivo de Ventas y Ganancias")
st.markdown("Este dashboard analiza la rentabilidad de las ventas, enfocándose en identificar las causas de las pérdidas en la región West.")

# Sidebar para Filtros globales
st.sidebar.header("Filtros Globales")
regiones = df['Region'].dropna().unique().tolist()
region_seleccionada = st.sidebar.selectbox("Selecciona una Región para análisis detallado", regiones, index=regiones.index('West') if 'West' in regiones else 0)

# --- SECCIÓN 1: Resumen General ---
st.header("📈 1. Resumen Estadístico y Distribuciones")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Métricas Clave del Dataset")
    st.write(df.describe())

with col2:
    st.subheader("Relación de Ventas vs Ganancias")
    fig_scatter, ax_scatter = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=df, x='Sales', y='Profit', alpha=0.5, color='darkviolet', ax=ax_scatter)
    ax_scatter.set_xscale('log')
    ax_scatter.set_title('Escala Logarítmica en Ventas')
    st.pyplot(fig_scatter)

# --- SECCIÓN 2: Análisis por Región ---
st.header("🗺️ 2. Proporción de Ganancias e Impacto por Estado")
col_pie, col_bar = st.columns(2)

with col_pie:
    st.subheader("Ganancias Totales (Profit) por Región")
    ganancias_por_region = df.groupby('Region')['Profit'].sum().reset_index()
    fig_pie, ax_pie = plt.subplots(figsize=(7, 7))
    ax_pie.pie(
        ganancias_por_region['Profit'],
        labels=ganancias_por_region['Region'],
        autopct='%1.1f%%',
        startangle=140,
        colors=sns.color_palette('pastel')[0:len(ganancias_por_region)],
        wedgeprops={'edgecolor': 'gray', 'linewidth': 1}
    )
    st.pyplot(fig_pie)

with col_bar:
    st.subheader(f"Desempeño por Estado en la Región: {region_seleccionada}")
    df_filtrado_reg = df[df['Region'] == region_seleccionada]
    ganancias_estado = df_filtrado_reg.groupby('State')['Profit'].sum().reset_index().sort_values(by='Profit', ascending=False)
    
    fig_bar, ax_bar = plt.subplots(figsize=(8, 6))
    sns.barplot(
        data=ganancias_estado,
        x='Profit',
        y='State',
        hue='State',
        palette='viridis',
        legend=False,
        ax=ax_bar
    )
    st.pyplot(fig_bar)

# --- SECCIÓN 3: Foco en Pérdidas (Colorado, Arizona, Oregon) ---
st.header("🔍 3. Investigación de Pérdidas en Colorado, Arizona y Oregon")
st.markdown("Análisis profundo del por qué estos tres estados de la región West presentan ganancias netas negativas.")

estados_criticos = ['Colorado', 'Arizona', 'Oregon']
df_criticos_perdida = df[(df['State'].isin(estados_criticos)) & (df['Profit'] < 0)]

# Mostrar tabla resumen interactiva
resumen_perdidas = df_criticos_perdida.groupby('State').agg(
    Total_Perdida=('Profit', 'sum'),
    Transacciones_Con_Perdida=('Profit', 'count'),
    Promedio_Perdida=('Profit', 'mean')
).reset_index().sort_values(by='Total_Perdida')

st.dataframe(resumen_perdidas.style.format({
    'Total_Perdida': '${:,.2f}',
    'Promedio_Perdida': '${:,.2f}'
}))

# Selector del estado para ver el detalle de categorías
estado_analisis = st.selectbox("Selecciona un estado crítico para auditar las causas de pérdida", estados_criticos)

df_estado_audit = df_criticos_perdida[df_criticos_perdida['State'] == estado_analisis]
analisis_cats = df_estado_audit.groupby(['Category', 'Sub-Category']).agg(
    Total_Perdida=('Profit', 'sum'),
    Ventas_Asociadas=('Sales', 'sum'),
    Descuento_Promedio=('Discount', 'mean')
).reset_index().sort_values(by='Total_Perdida')

col_tabla, col_desc = st.columns([2, 1])

with col_tabla:
    st.subheader(f"Subcategorías más afectadas en {estado_analisis}")
    st.dataframe(analisis_cats.style.format({
        'Total_Perdida': '${:,.2f}',
        'Ventas_Asociadas': '${:,.2f}',
        'Descuento_Promedio': '{:.1%}'
    }))

with col_desc:
    st.subheader("💡 Diagnóstico Operativo")
    max_descuento_prom = analisis_cats['Descuento_Promedio'].max()
    st.info(
        f"En **{estado_analisis}**, las mayores pérdidas ocurren en categorías con descuentos de hasta el **{max_descuento_prom:.0%}**. "
        "La combinación de productos de alto valor unitario con descuentos agresivos está erosionando la rentabilidad de las sucursales."
    )
