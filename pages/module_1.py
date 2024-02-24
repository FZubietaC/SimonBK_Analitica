# imports functions base
import streamlit as st
import pandas as pd
import numpy as np
import folium
import datetime


# imports custom functions
from conections import connect_to_postgresql
from streamlit_folium import folium_static


# Llamar a la función de conexión desde connection.py
conexion = connect_to_postgresql()

# Realizar operaciones con la conexión si es exitosa
if conexion:
    # ejecutar una consulta
    cursor_avl_records = conexion.cursor()
    cursor_avl_records.execute("SELECT * FROM avl_records;")
    rows_avl_records = cursor_avl_records.fetchall()
    columns_avl_records = [column[0] for column in cursor_avl_records.description]
    # Transformar los datos en un Dataframe
    data_avl_records = pd.DataFrame.from_records(rows_avl_records,columns=columns_avl_records)
    # Cerrar cursor y conexión
    cursor_avl_records.close()
    conexion.close()
else:
    print("No se pudo establecer la conexión a PostgreSQL.")

# Verificacion de carga de informacion.
data_load_state = st.text('Loading data...')
# Cargar los datos de la tabla.
# Notificacion de informacion cargada de forma satisfactoria.
data_load_state.text('Loading data...done!')

data_avl_records['latitude'] = pd.to_numeric(data_avl_records['latitude'].astype(np.float32))
data_avl_records['longitude'] = pd.to_numeric(data_avl_records['longitude'].astype(np.float32))
data_avl_records['time_stamp_event'] = pd.to_datetime(data_avl_records['time_stamp_event'], errors='coerce')

#Creación del filtro por placa
unique_plates = data_avl_records['plate'].unique()
letras_permitidas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
# Filtrar placas que comienzan con una letra permitida
placas_filtradas = [placa for placa in unique_plates if placa and placa[0].upper() in letras_permitidas]

selected_plate = st.selectbox("Selecciona una placa:", placas_filtradas)
  
col1, col2 = st.columns(2)  
with col1: 
    start_date = st.date_input("Selecciona la fecha de inicio", min_value=data_avl_records['time_stamp_event'].min().date(), max_value=data_avl_records['time_stamp_event'].max().date())


with col2:
    end_date = st.date_input("Selecciona la fecha de fin", min_value=data_avl_records['time_stamp_event'].min().date(), max_value=data_avl_records['time_stamp_event'].max().date())

# Convertir las fechas a tipo datetime64[ns]
start_date = datetime.datetime(start_date.year, start_date.month, start_date.day)
end_date = datetime.datetime(end_date.year, end_date.month, end_date.day)

# Filtrar datos según las fechas y la placa seleccionada
filtered_data_combined = data_avl_records[(data_avl_records['plate'] == selected_plate) & (data_avl_records['time_stamp_event'] >= start_date) & (data_avl_records['time_stamp_event'] < (end_date + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)))]

display_mode = st.radio("Selecciona el modo de visualización:", ["Puntos", "Puntos + Líneas"])


# Verificar si hay datos después de aplicar el filtro de placa y fecha
if not filtered_data_combined.empty:
    # Resto del código para el filtrado y visualización del mapa
    mapa_combined = folium.Map(
        location=[filtered_data_combined['latitude'].mean(), filtered_data_combined['longitude'].mean()],
        zoom_start=14,
        tiles='https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
        attr='©CartoDB'
    )

    if display_mode == "Puntos + Líneas":
        # Obtener las coordenadas de los puntos
        locations = filtered_data_combined[['latitude', 'longitude']].values

        # Crear un objeto PolyLine para trazar la ruta
        polyline = folium.PolyLine(
            locations=locations,
            color='red',
            weight=2,
            opacity=1
        ).add_to(mapa_combined)

        # Añadir círculo al final de la línea para resaltar la última posición
        folium.CircleMarker(
            location=locations[-1],
            radius=5,
            color='green',
            fill=True,
            fill_color='green',
            fill_opacity=1.0,
            popup=f'''
                <div style="white-space: nowrap;">
                    <b>Última posición:</b><br>
                    <b>Fecha evento:</b> {filtered_data_combined.iloc[-1]["time_stamp_event"]}<br>
                    <b>Velocidad:</b> {filtered_data_combined.iloc[-1]["speed"]} Km/h
                </div>
                '''
            ).add_to(mapa_combined)

        # Añadir círculo al inicio de la línea para resaltar la primera posición
        folium.CircleMarker(
            location=locations[0],
            radius=5,
            color='orange',
            fill=True,
            fill_color='orange',
            fill_opacity=1.0,
            popup=f'''
                <div style="white-space: nowrap;">
                    <b>Primera posición:</b><br>
                    <b>Fecha evento:</b> {filtered_data_combined.iloc[0]["time_stamp_event"]}<br>
                    <b>Velocidad:</b> {filtered_data_combined.iloc[0]["speed"]} Km/h
                </div>
                '''
            ).add_to(mapa_combined)

    for index, row in filtered_data_combined.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=3,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=1.0,
            popup=f'''
                <div style="white-space: nowrap;">
                    <b>Imei:</b> {row["imei"]}<br>
                    <b>Placa:</b> {row["plate"]}<br>
                    <b>Fecha evento:</b> {row["time_stamp_event"]}<br>
                    <b>Evento:</b> {row["event"]}<br>
                    <b>Velocidad:</b> {row["speed"]} Km/h
                </div>
                '''
            ).add_to(mapa_combined)
    
    # Mostrar el mapa en Streamlit usando st.pydeck_chart
    folium_static(mapa_combined)
else:
    st.warning("No hay registros para la placa y fecha seleccionadas.")

    
