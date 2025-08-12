import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 1. Configuración de la página ---
st.set_page_config(layout="wide")
st.title('🚗 Análisis de Vehículos Usados')
st.write('Explora los datos de vehículos usados de manera interactiva.')
st.markdown("---")

# --- 2. Cargar y preparar los datos (con caché y manejo de errores) ---


@st.cache
def load_data():
    """
    Carga, limpia y traduce el archivo de datos.
    Esta función se ejecuta solo una vez gracias a @st.cache_data.
    """
    # Asegúrate de que el archivo 'vehicles_us.csv' esté en la misma carpeta que 'app.py'
    file_path = 'vehicles_us.csv'
    if not os.path.exists(file_path):
        st.error(
            f"Error: No se encontró el archivo de datos en la ruta: {file_path}")
        st.stop()

    car_data = pd.read_csv(file_path)

    # Manejar valores nulos
    car_data['model_year'].fillna(
        car_data['model_year'].median(), inplace=True)
    car_data['odometer'].fillna(car_data['odometer'].median(), inplace=True)

    # Traducir los valores de la columna 'condition' a español
    traducciones_condicion = {
        'new': 'nuevo',
        'like new': 'casi nuevo',
        'excellent': 'excelente',
        'good': 'bueno',
        'fair': 'justo',
        'salvage': 'rescatado'
    }
    car_data['condition'] = car_data['condition'].map(
        traducciones_condicion).fillna(car_data['condition'])

    return car_data


car_data = load_data()

# --- 3. Definir paleta de colores y filtros ---
# Paleta de colores elegante y sutil
colores_sutiles = {
    'nuevo': '#607D8B',         # Gris Pizarra
    'casi nuevo': '#4DB6AC',    # Turquesa
    'excelente': '#81C784',     # Verde Pastel
    'bueno': '#FFB74D',         # Naranja Ámbar
    'justo': '#FF8A65',         # Naranja Coral
    'rescatado': '#E57373'      # Rojo Suave
}

# Elementos interactivos (filtros en la barra lateral)
st.sidebar.header('Filtros de Datos')

# Filtro por tipo de vehículo
tipos_vehiculos = sorted(car_data['type'].unique().tolist())
tipo_seleccionado = st.sidebar.selectbox(
    'Selecciona un tipo de vehículo:',
    ['Todos'] + tipos_vehiculos
)

# Filtro por rango de año
min_year = int(car_data['model_year'].min())
max_year = int(car_data['model_year'].max())
rango_año = st.sidebar.slider(
    'Selecciona un rango de año:',
    min_year,
    max_year,
    (min_year, max_year)
)

# Aplicar filtros
if tipo_seleccionado != 'Todos':
    filtered_data = car_data[car_data['type'] == tipo_seleccionado]
else:
    filtered_data = car_data

filtered_data = filtered_data[
    (filtered_data['model_year'] >= rango_año[0]) & (
        filtered_data['model_year'] <= rango_año[1])
]

# Filtro por modelo de vehículo (marca/agencia)
modelos_disponibles = sorted(filtered_data['model'].unique().tolist())
modelo_seleccionado = st.sidebar.selectbox(
    'Selecciona un modelo de vehículo:',
    ['Todos'] + modelos_disponibles
)

if modelo_seleccionado != 'Todos':
    filtered_data = filtered_data[filtered_data['model']
                                  == modelo_seleccionado]

# --- 4. Casillas de verificación para mostrar/ocultar gráficos ---
st.header('Visualizaciones')
st.markdown("Selecciona los gráficos que deseas ver:")
mostrar_histograma_año = st.checkbox('Histograma de Años del Modelo')
mostrar_dispersion = st.checkbox(
    'Gráfico de Dispersión: Precio vs Kilometraje')
mostrar_histograma_condicion = st.checkbox('Histograma de la Condición')
mostrar_barras_modelo = st.checkbox(
    'Gráfico de Barras: Precio Promedio por Modelo')
st.markdown("---")

# --- 5. Validar datos antes de generar gráficos ---
if filtered_data.empty:
    st.warning("No hay datos disponibles para los filtros seleccionados.")
    st.info("Intenta ajustar los filtros para ver los resultados.")
else:
    # --- 6. Generar y mostrar los gráficos según la selección ---
    if mostrar_histograma_año:
        st.subheader('📊 Distribución de Años del Modelo por Condición')
        st.write('Este gráfico muestra la distribución de los vehículos por año, ayudando a identificar la antigüedad de la mayoría de los coches en el mercado.')
        fig1 = px.histogram(filtered_data, x='model_year', color='condition',
                            title='Distribución de Años del Modelo por Condición',
                            labels={'model_year': 'Año del Modelo',
                                    'count': 'Cantidad', 'condition': 'Condición'},
                            color_discrete_map=colores_sutiles)

        fig1.update_layout(title_font_size=16, title_x=0.5,
                           plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("---")

    if mostrar_dispersion:
        st.subheader('🔍 Relación entre Precio y Kilometraje por Condición')
        st.write(
            'Este gráfico muestra la relación entre el precio del vehículo y su kilometraje.')

        fig2 = px.scatter(filtered_data, x='odometer', y='price', color='condition',
                          title='Relación entre Precio y Kilometraje por Condición',
                          labels={'odometer': 'Kilometraje',
                                  'price': 'Precio ($)', 'condition': 'Condición'},
                          opacity=0.7,
                          color_discrete_map=colores_sutiles)

        fig2.update_layout(title_font_size=16, title_x=0.5,
                           plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("---")

    if mostrar_histograma_condicion:
        st.subheader('🚗 Distribución de la Condición de los Vehículos')
        st.write('Este gráfico te permite ver la cantidad de vehículos disponibles según su condición, lo cual es útil para entender la calidad general de la oferta.')
        fig3 = px.histogram(filtered_data, x='condition', color='condition',
                            title='Distribución de la Condición de los Vehículos',
                            labels={'condition': 'Condición',
                                    'count': 'Cantidad'},
                            category_orders={'condition': [
                                'nuevo', 'casi nuevo', 'excelente', 'bueno', 'justo', 'rescatado']},
                            color_discrete_map=colores_sutiles)

        fig3.update_layout(title_font_size=16, title_x=0.5,
                           plot_bgcolor='white', paper_bgcolor='white', showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("---")

    if mostrar_barras_modelo:
        st.subheader('📈 Precio Promedio por Modelo')
        st.write('Este gráfico compara el precio promedio de los vehículos por marca y modelo, ayudando a los usuarios a evaluar el valor relativo de cada uno.')

        # Calcular el precio promedio por modelo y ordenar
        precio_promedio_modelo = filtered_data.groupby(
            'model')['price'].mean().reset_index().sort_values('price', ascending=False)
        fig4 = px.bar(precio_promedio_modelo, x='model', y='price',
                      title='Precio Promedio por Modelo',
                      labels={'model': 'Modelo del Vehículo',
                              'price': 'Precio Promedio ($)'},
                      color='price', color_continuous_scale=px.colors.sequential.Teal)

        fig4.update_layout(title_font_size=16, title_x=0.5,
                           plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown("---")
