import streamlit as st 
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from PIL import Image
from sklearn.preprocessing import MinMaxScaler

warnings.filterwarnings('ignore')

from funciones import *

def main():
    #from functions import *
    min_minutos = 99999999
    st.set_page_config(layout="wide")

    st.title("Convocatorias selecciones EURO2021 en función del Big Data")

    st.sidebar.title("Opciones de configuración")
    
    menu = st.sidebar.selectbox('Menu', 
                                ['Información',
                                 'Once ideal', 
                                 'Once ideal por países', 
                                 'Convocatorias ideales',
                                ])

    #with st.form(key = "form1"):
    # form = st.sidebar.form(key = "formulario")

    #name = form.text_input(label = "Enter team")

    if menu == 'Información':
        st.header('Información de la aplicación')

        st.subheader('Descripción general')
        st.write('Esta aplicación nos permite seleccionar los 11 ideales de la Eurocopa, tanto del conjunto de los equipos como de las diferentes selecciones por separado.')
        st.write('Utilizando la analítica avanzada se han conseguido dar una valoración a todos los jugadores en función de los parámetros de interés según su posición. Además se han tenido en cuenta diferentes posibles estilos de juego que puede seleccionar el usuario.')
       
        st.subheader('Información adicional')

        st.write("Esta aplicación se ha desarrollado como Trabajo de Fin de Experto en Big Data Aplicado al modelo de juego, análisis y entrenamiento en Fútbol")
        
        
        c1, c2, c3 = st.beta_columns([1, 6, 1])
        c1.write('')
        image = Image.open('sdc.png')
        c2.image(image, caption='Sport Data Campus')
        c3.write('')

        st.write('Agradecimiento especial al profesor Javier Fernández por su ayuda en la realización de este proyecto')

    elif menu == 'Once ideal':

        estilodejuego = st.sidebar.selectbox('Seleccionar estilo de juego', ['Combinativo', 'Directo', 'Mixto'], key="estilodejuego")
        
        formacion = st.sidebar.selectbox('Elige la formación que desea', ['4-4-2', '4-3-3', '5-4-1', '3-5-2'], key="formacion")

        with st.sidebar.beta_expander('Filters'):
            min_minutos = st.slider("Mínimo de minutos jugados", min_value = 1, max_value = 6000, value = 1000)
            values = st.slider("Rango de  valor de mercado (en €)", min_value = 1, max_value = 200000000, value = (40000000, 200000000), step = 200000)
            min_valor = values[0]
            max_valor = values[1]
           
            edades = st.slider("Rango de edades", min_value = 16, max_value = 40, value = (16, 40))
            min_edad = edades[0]
            max_edad = edades[1]

        col1, col2 = st.beta_columns([2, 2])

        col1.subheader("Once ideal colocado en el terreno de juego")
        col1.pyplot(once_ideal_eurocopa(estilodejuego, min_minutos, min_valor, max_valor, min_edad, max_edad, formacion)[0])

        col2.subheader("Jugadores del once inicial con su valoración")
        col2.dataframe(once_ideal_eurocopa(estilodejuego, min_minutos, min_valor, max_valor, min_edad, max_edad, formacion)[1])
        col2.write("Los valores obtenidos se han calculado a traves de una serie de métricas seleccionadas y ponderadas en función del estilo de juego seleccionado y la posición de los jugadores. ")
        col2.write("Todas las métricas a su vez han sido normalizadas entre 0 y 1, con el normalizador min-max. De modo que el valor máximo posible es de 10 puntos.")
        
    elif menu == 'Once ideal por países': 

        estilodejuego = st.sidebar.selectbox('Seleccionar estilo de juego', ['Combinativo', 'Directo', 'Mixto'], key="estilodejuego")       
        seleccion = st.sidebar.selectbox('Elige tu selección', ['Alemania', 'Austria', 'Bélgica', 'Croacia',
                                                          'Dinamarca', 'Escocia', 'Eslovaquia', 'España',
                                                          'Finlandia', 'Francia', 'Hungría', 'Inglaterra',
                                                          'Italia', 'Macedonia del Norte', 'País de Gales', 'Países Bajos',
                                                          'Polonia', 'Portugal', 'República Checa', 'Rusia',
                                                          'Suecia', 'Suiza', 'Turquía', 'Ucrania',                 
                                                           ], key="seleccion")



        formacion = st.sidebar.selectbox('Elige la formación que desea', ['4-4-2', '4-3-3', '5-4-1', '3-5-2'], key="formacion")

        with st.sidebar.beta_expander('Filters'):
            min_minutos = st.slider("Mínimo de minutos jugados", min_value = 1, max_value = 6000, value = 1000)
            values = st.slider("Rango de  valor de mercado (en €)", min_value = 1, max_value = 200000000, value = (2000000, 200000000), step = 200000)
            min_valor = values[0]
            max_valor = values[1]
            edades = st.slider("Rango de edades", min_value = 16, max_value = 40, value = (16, 40))
            min_edad = edades[0]
            max_edad = edades[1]

        col1, col2 = st.beta_columns([2, 2])

        col1.subheader("Once ideal colocado en el terreno de juego")
        col1.pyplot(once_ideal_pais(estilodejuego, seleccion, min_minutos, min_valor, max_valor, min_edad, max_edad, formacion)[0])

        col2.subheader("Jugadores del once inicial con su valoración")
        col2.dataframe(once_ideal_pais(estilodejuego, seleccion, min_minutos, min_valor, max_valor, min_edad, max_edad, formacion)[1])
        col2.write("Los valores obtenidos se han calculado a traves de una serie de métricas seleccionadas y ponderadas en función del estilo de juego seleccionado y la posición de los jugadores. ")
        col2.write("Todas las métricas a su vez han sido normalizadas entre 0 y 1, con el normalizador min-max. De modo que el valor máximo posible es de 10 puntos.")
        
        st.write('Es recomendable ajustar el valor de mercado mínimo de los jugadores teniendo en cuenta el nivel de sus ligas')
    elif menu == 'Convocatorias ideales': 

        estilodejuego = st.sidebar.selectbox('Seleccionar estilo de juego', ['Combinativo', 'Directo', 'Mixto'], key="estilodejuego")       
        seleccion = st.sidebar.selectbox('Elige tu selección', ['Alemania', 'Austria', 'Bélgica', 'Croacia',
                                                          'Dinamarca', 'Escocia', 'Eslovaquia', 'España',
                                                          'Finlandia', 'Francia', 'Hungría', 'Inglaterra',
                                                          'Italia', 'Macedonia del Norte', 'País de Gales', 'Países Bajos',
                                                          'Polonia', 'Portugal', 'República Checa', 'Rusia',
                                                          'Suecia', 'Suiza', 'Turquía', 'Ucrania',                 
                                                           ], key="seleccion")
 

        
        n_porteros = st.sidebar.slider("Elige el número de porteros que desea introducir en la convocatoria", min_value = 1, max_value = 5, value = 3)
        n_defensas = st.sidebar.slider("Elige el número de defensas centrales que desea introducir en la convocatoria", min_value = 1, max_value = 7, value = 5)
        n_laterales = st.sidebar.slider("Elige el número de laterales que desea introducir en la convocatoria", min_value = 1, max_value = 7, value = 4)
        n_medios = st.sidebar.slider("Elige el número de centrocampistas que desea introducir en la convocatoria", min_value = 1, max_value = 7, value = 4)
        n_bandas = st.sidebar.slider("Elige el número de extremos que desea introducir en la convocatoria", min_value = 1, max_value = 7, value = 5)
        n_delanteros = st.sidebar.slider("Elige el número de delanteros que desea introducir en la convocatoria", min_value = 1, max_value = 7, value = 4)


        with st.sidebar.beta_expander('Filters'):
            min_minutos = st.slider("Mínimo de minutos jugados", min_value = 1, max_value = 6000, value = 1000)
            values = st.slider("Rango de  valor de mercado (en €)", min_value = 1, max_value = 200000000, value = (2000000, 170000000), step = 200000)
            min_valor = values[0]
            max_valor = values[1]
            edades = st.slider("Rango de edades", min_value = 16, max_value = 40, value = (16, 40))
            min_edad = edades[0]
            max_edad = edades[1]

        if (n_porteros + n_defensas + n_laterales + n_medios + n_bandas + n_delanteros) > 25:
            st.warning("Error. Has excedido el número máximo de jugadores de la convocatoria (25)")
            st.write("Por favor, seleccione menos cantidad de jugadores en las diferentes posiciones para tener un total de menos de 25")
        else:
            st.subheader("Convocatoria ideal de " + seleccion)
            st.table(convocatoria_ideal_pais(estilodejuego, seleccion, n_porteros, n_defensas, n_laterales, n_medios, n_bandas, n_delanteros,
                                            min_minutos, min_valor, max_valor, min_edad, max_edad
                                            ))
                                            
        st.write('Es recomendable ajustar el valor de mercado mínimo de los jugadores teniendo en cuenta el nivel de sus ligas')
    # submit = st.sidebar.form_submit_button(label = "Continuar")

    

if __name__ == "__main__":
    main()