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


def search_pos(pos, data):   
    
    dataf = data[data['Posición específica'] == pos]
    
    return dataf

# nation_b = []
# nation = []

def search_nation(nation, data):
    lista_datapais = []
    for pos_data in data: 
        datapais = pos_data[(pos_data['Pasaporte'] == nation)]
#         datapais = pos_data[(pos_data['Pasaporte'].find(nation) > 0)]
        lista_datapais.extend([datapais])
    # hay que intentar coger de los que tengan 2 pasaportes
    return lista_datapais


# def normalize(data):
#     data_norm = []
#     data_trans = np.transpose(data)
#     for j in data_trans:
#         data_norm_i = (j - data_trans.min())/(data_trans.max()-data_trans.min())
#         data_norm.append(data_norm_i)
    
#     data_norm_trans = np.transpose(data_norm)
# #     print(data_norm_trans)
#     return data_norm_trans

def once_inicial(jugadores, formacion):
    if formacion == '4-3-3':
        once_ideal = jugadores[0][:1]
        once_ideal = once_ideal.append(jugadores[1][:2])
        once_ideal = once_ideal.append(jugadores[2][:2])
        once_ideal = once_ideal.append(jugadores[3][:3])
        once_ideal = once_ideal.append(jugadores[4][:2])
        once_ideal = once_ideal.append(jugadores[5][:1])
    elif formacion == '5-4-1':
        once_ideal = jugadores[0][:1]
        once_ideal = once_ideal.append(jugadores[1][:2])
        once_ideal = once_ideal.append(jugadores[2][:3])
        once_ideal = once_ideal.append(jugadores[3][:2])
        once_ideal = once_ideal.append(jugadores[4][:2])
        once_ideal = once_ideal.append(jugadores[5][:1])
    elif formacion == '3-5-2':
        once_ideal = jugadores[0][:1]
        once_ideal = once_ideal.append(jugadores[4][:2])
        once_ideal = once_ideal.append(jugadores[2][:3])
        once_ideal = once_ideal.append(jugadores[3][:3])
        once_ideal = once_ideal.append(jugadores[5][:2])
    else:
        once_ideal = jugadores[0][:1]
        once_ideal = once_ideal.append(jugadores[1][:2])
        once_ideal = once_ideal.append(jugadores[2][:2])
        once_ideal = once_ideal.append(jugadores[3][:2])
        once_ideal = once_ideal.append(jugadores[4][:2])
        once_ideal = once_ideal.append(jugadores[5][:2])

    once_ideal.reset_index(drop=True, inplace=True)
    once_ideal.index = np.arange(1, len(once_ideal) + 1)
    return once_ideal

def convocatoria_ideal(jugadores, n_porteros, n_defensas, n_laterales, n_medios, n_bandas, n_delanteros):
    
    convocatoria = jugadores[0][:n_porteros]
    convocatoria = convocatoria.append(jugadores[1][:n_defensas])
    convocatoria = convocatoria.append(jugadores[2][:n_laterales])
    convocatoria = convocatoria.append(jugadores[3][:n_medios])
    convocatoria = convocatoria.append(jugadores[4][:n_bandas])
    convocatoria = convocatoria.append(jugadores[5][:n_delanteros])

    convocatoria.reset_index(drop=True, inplace=True)
    convocatoria.index = np.arange(1, len(convocatoria) + 1)
    return convocatoria

def select_metrics(pos):
    #10 METRICAS EN CADA POSICIÓN
    if pos == 'GK':
        metricas = ['Inverso Goles recibidos/90', 'Paradas, %', 'Goles evitados/90', 'Pases/90','Salidas/90',
            'Duelos aéreos en los 90 porteros','Pases cortos / medios /90', 'Pases largos/90', 'Precisión pases largos, %', 'Precisión pases, %']
    elif pos == 'LAT':
        metricas = ['Acciones defensivas realizadas/90', 'Centros/90', 'Duelos defensivos/90','Duelos defensivos ganados, %',
            'Pases/90', 'Pases hacia adelante/90','Precisión pases hacia adelante, %', 'Precisión centros, %', 'Pases en el último tercio/90', 'Duelos aéreos ganados, %']
    elif pos == 'DFC':
        metricas = ['Acciones defensivas realizadas/90', 'Duelos aéreos en los 90', 'Duelos aéreos ganados, %','Pases largos/90',
            'Pases hacia adelante/90', 'Precisión pases hacia adelante, %','Pases/90', 'Precisión pases, %', 'Duelos defensivos/90', 'Duelos defensivos ganados, %']      
    elif pos == 'MC':
        metricas = ['Acciones defensivas realizadas/90', 'Duelos aéreos en los 90', 'Duelos aéreos ganados, %','Duelos defensivos ganados, %',
            'Pases/90', 'Precisión pases, %','Pases cortos / medios /90', 'Pases largos/90', 'Interceptaciones/90', 'Goles']
    elif pos == 'IDM':
        metricas = ['Duelos atacantes/90', 'Duelos atacantes ganados, %', 'Pases al área de penalti/90','Regates/90',
            'Pases en profundidad/90','Asistencias', 'Jugadas claves/90', 'Centros/90','Precisión centros, %','Goles']
    elif pos == 'DC':
        metricas = ['Goles', 'Asistencias', 'Duelos aéreos en los 90', 'Duelos aéreos ganados, %','Tiros a la portería, %',
            'Remates/90', 'Regates/90','Toques en el área de penalti/90', 'Pases en el último tercio/90', 'Precisión pases en el último tercio, %']
    else:
        print('Error, posición incorrecta') 
    return metricas

def values_position(estilo, pos):
    val = []
    if estilo == 'Combinativo':
        if pos == 'GK':
            val = [0.15,0.1,0.1,0.2,0.05,0.05,0.2,0.02,0.03,0.1]      
        elif pos == 'LAT':
            val = [0.08,0.07,0.08,0.07,0.25,0.07,0.1,0.08,0.12,0.08]
        elif pos == 'DFC':
            val = [0.08,0.08,0.12,0.07,0.07,0.08,0.15,0.15,0.08,0.12]
        elif pos == 'MC':
            val = [0.05,0.03,0.07,0.1,0.2,0.15,0.14,0.06,0.1,0.1]
        elif pos == 'IDM':
            val = [0.05,0.12,0.18,0.1,0.05,0.15,0.1,0.03,0.07,0.15]
        elif pos == 'DC':
            val = [0.25,0.13,0.03,0.07,0.05,0.05,0.05,0.15,0.1,0.12]
            # val = [1,0,0,0,0,0,0,0,0,0]
        else:
            val = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
            print('Error, posición incorrecta')
            
    elif estilo == 'Directo':
        if pos == 'GK':
            val = [0.15,0.1,0.1,0.05,0.1,0.1,0.05,0.15,0.15,0.05]       
        elif pos == 'LAT':
            val = [0.05,0.12,0.1,0.1,0.05,0.2,0.1,0.13,0.05,0.1]
        elif pos == 'DFC':
            val = [0.08,0.08,0.12,0.14,0.12,0.12,0.05,0.07,0.1,0.12]
        elif pos == 'MC':
            val = [0.1,0.08,0.12,0.1,0.08,0.07,0.08,0.17,0.1,0.1]
        elif pos == 'IDM':
            val = [0.1,0.15,0.07,0.05,0.1,0.08,0.1,0.08,0.12,0.15]
        elif pos == 'DC':
            val = [0.25,0.13,0.14,0.15,0.07,0.08,0.05,0.05,0.02,0.05]
        else:
            val = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
            print('Error, posición incorrecta') 
    
    elif estilo == 'Mixto':
        if pos == 'GK':
            val = [0.15,0.1,0.1,0.12,0.07,0.08,0.13,0.09,0.09,0.07]       
        elif pos == 'LAT':
            val = [0.07,0.09,0.09,0.08,0.15,0.13,0.10,0.11,0.09,0.09]
        elif pos == 'DFC':
            val = [0.08,0.08,0.12,0.1,0.1,0.1,0.1,0.11,0.09,0.12]
        elif pos == 'MC':  
            val = [0.07,0.05,0.1,0.1,0.14,0.11,0.11,0.12,0.1,0.1]
        elif pos == 'IDM': 
            val = [0.08,0.13,0.12,0.08,0.07,0.12,0.1,0.05,0.1,0.15]
        elif pos == 'DC':
            val = [0.25,0.13,0.08,0.11,0.06,0.07,0.05,0.1,0.06,0.09]
        else:
            val = [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
            print('Error, posición incorrecta')   
    else:
        print('Error, estilo de juego incorrecto')
    return val


def load_data(estilo, min_minutes, min_value, max_value, min_edad, max_edad):
    data = pd.read_csv('Jugadores selecciones (1).csv', sep=";", encoding='utf-8')
    data = data.fillna('0')
    datos = []

    for l in data['Posición específica']:
        datos.append(l.split(sep=',')[0])

    data['Posición específica'] = datos

    dict_posiciones = {'0': 'No disponible', 'GK': 'GK', 'RB': 'LAT', 'LB': 'LAT',  'LCB': 'DFC', 'RCB': 'DFC', 'CB': 'DFC', 'AMF': 'MC', 
                       'LCMF': 'MC', 'LDMF': 'MC', 'RDMF': 'MC', 'DMF': 'MC', 'RCMF': 'MC', 'RW': 'IDM', 'LW': 'IDM', 'LAMF': 'IDM', 'RAMF': 'IDM', 'CF': 'DC'}

    data['Posición específica'] = data['Posición específica'].map(dict_posiciones)

    posiciones = ['GK', 'LAT', 'DFC', 'MC', 'IDM', 'DC']
    datospos = []
    jugadores = []
    jugadores_pais = []

    for pos in posiciones :  
        datospos = search_pos(pos,data)
        metricaspos = select_metrics(pos)
        ranges = []
        values = datospos[['Jugador', 'Equipo', 'Posición específica', 'Pasaporte', 'Minutos jugados', 'Valor de mercado', 'Edad']+metricaspos].values.tolist()
        values_pos = values_position(estilo, pos)


        values_metrics = []

        for l in values:
            l[7:] = [float(x) for x in l[7:]]
            values_metrics.append(l[7:])

        minmax = MinMaxScaler()
        values_metrics_norm = minmax.fit_transform(values_metrics)
        # values_metrics_norm = normalize(values_metrics)

        suma_players = []

        for values_metrics_np_i in values_metrics_norm:
            values_metrics_np_i = np.array(values_metrics_np_i)
            values_pos_np = np.array(values_pos)
            info_player = values_metrics_np_i * values_pos_np
            suma_player = info_player.sum()*10
            suma_players.append(suma_player)


        # lista = datospos[['Jugador', 'Equipo','Posición específica', 'Pasaporte']].values.tolist()
#         print("Número de "+pos+":" , datospos.shape[0])
        lista = datospos[['Jugador', 'Equipo','Posición específica', 'Pasaporte', 'Minutos jugados', 'Valor de mercado', 'Edad']]
        lista['value'] = suma_players
        datos2= []
        for j in lista['Pasaporte']:
            datos2.append(j.split(sep=',')[0])

        lista['Pasaporte'] = datos2

        dict_pasaporte = {'Italy': 'Italia', 'Turkey': 'Turquía', 'Wales': 'País de Gales', 'Switzerland': 'Suiza',
                           'Belgium': 'Bélgica', 'Russia': 'Rusia', 'Denmark': 'Dinamarca', 'Finland': 'Finlandia',
                           'Ukraine': 'Ucrania', 'Netherlands': 'Países Bajos', 'Austria': 'Austria', 'North Macedonia': 'Macedonia del Norte',
                           'England': 'Inglaterra', 'Croatia': 'Croacia', 'Czech Republic': 'República Checa', 'Scotland': 'Escocia',
                           'Spain': 'España', 'Sweden': 'Suecia', 'Poland': 'Polonia', 'Slovakia': 'Eslovaquia',
                           'Germany': 'Alemania', 'Portugal': 'Portugal', 'France': 'Francia', 'Hungary': 'Hungría', '0': 'Sin País'}

        lista['Pasaporte'] = lista['Pasaporte'].map(dict_pasaporte) 
        lista = lista.sort_values(by = 'value',  ascending = False)

        if min_minutes < 10000:
            lista = lista[lista['Minutos jugados'] >= min_minutes]

        lista = lista[lista['Valor de mercado'] >= min_value]

        lista = lista[lista['Valor de mercado'] <= max_value]


        lista['Edad'] = lista['Edad'].astype(int)
        lista = lista[lista['Edad'] >= min_edad]
        lista = lista[lista['Edad'] <= max_edad]

#         print(lista)
        jugadores.extend([lista])
#         jugadores.append(lista)
#         jugadores.extend(lista)
#         jugadores.append([lista])
        
    return jugadores

def once_ideal_eurocopa(estilo,minimo_minutos, min_value, max_value, min_edad, max_edad, formacion):
    data = load_data(estilo,minimo_minutos, min_value, max_value, min_edad, max_edad)
    once_eurocopa = once_inicial(data, formacion)
    once_eurocopa = once_eurocopa.drop(['Minutos jugados','Posición específica','Valor de mercado'],axis=1)
    imagen_once = draw_pitch(once_eurocopa, formacion)
    once_final = [imagen_once,once_eurocopa]
    return once_final

def once_ideal_pais(estilo, nation, minimo_minutos, min_value, max_value, min_edad, max_edad, formacion):
    data = load_data(estilo, minimo_minutos, min_value, max_value, min_edad, max_edad)
    lista_nation = search_nation(nation, data)
    once_pais = once_inicial(lista_nation, formacion)
    once_pais = once_pais.drop(['Pasaporte','Minutos jugados','Posición específica'],axis=1)
    imagen_once_pais = draw_pitch(once_pais, formacion)
    once_final_pais = [imagen_once_pais, once_pais]
    return once_final_pais
    
    
def convocatoria_ideal_pais(estilo, nation, n_porteros, n_defensas, n_laterales, n_medios, n_bandas, n_delanteros, minimo_minutos
                            , min_value, max_value, min_edad, max_edad):
    data = load_data(estilo, minimo_minutos, min_value, max_value, min_edad, max_edad)
    lista_nation = search_nation(nation, data)
    convocatoria_eurocopa = convocatoria_ideal(lista_nation, n_porteros, n_defensas, n_laterales, n_medios, n_bandas, n_delanteros)
    convocatoria_eurocopa = convocatoria_eurocopa.drop(['Pasaporte','Minutos jugados'],axis=1)
    return convocatoria_eurocopa

def draw_pitch(jugadores, formacion):

    line = "#faf0e6"
    pitch = "#299c05"
    
    fig,ax = plt.subplots(figsize=(10.4,6.8))
    plt.xlim(-1,101)
    plt.ylim(-1,101)
    ax.axis('off')

    # lineas campo
    ly1 = [0,0,100,100,0]
    lx1 = [0,100,100,0,0]

    plt.plot(lx1,ly1,color=line,zorder=5)

    # area grande
    ly2 = [21.1,21.1,78.9,78.9] 
    lx2 = [100,83,83,100]
    plt.plot(lx2,ly2,color=line,zorder=3)

    ly3 = [21.1,21.1,78.9,78.9] 
    lx3 = [0,17,17,0]
    plt.plot(lx3,ly3,color=line,zorder=3)

    # porteria
    ly4 = [43.4,43.4,56.6,56.6]
    lx4 = [100,100.2,100.2,100]
    plt.plot(lx4,ly4,color=line,zorder=3)

    ly5 = [43.4,43.4,56.6,56.6]
    lx5 = [0,-0.2,-0.2,0]
    plt.plot(lx5,ly5,color=line,zorder=3)

    # area pequeña
    ly6 = [36.8,36.8,63.2,63.2]
    lx6 = [100,94.2,94.2,100]
    plt.plot(lx6,ly6,color=line,zorder=3)

    ly7 = [36.8,36.8,63.2,63.2]
    lx7 = [0,5.8,5.8,0]
    plt.plot(lx7,ly7,color=line,zorder=3)

    # lineas y puntos
    vcy5 = [0,100] 
    vcx5 = [50,50]
    plt.plot(vcx5,vcy5,color=line,zorder=3)

    plt.scatter(88.5,50,color=line,zorder=3)
    plt.scatter(11.5,50,color=line,zorder=3)
    plt.scatter(50,50,color=line,zorder=3)
    
    
    # circulos
    circle1 = plt.Circle((89,50), 9.15,ls='solid',lw=1.5,color=line, fill=False, zorder=1,alpha=1)
    circle2 = plt.Circle((11,50), 9.15,ls='solid',lw=1.5,color=line, fill=False, zorder=1,alpha=1)
    circle3 = plt.Circle((50,50), 9.15,ls='solid',lw=1.5,color=line, fill=False, zorder=2,alpha=1)
    
    
    # textos
    if len(jugadores) < 11 :
        text_error = plt.text(0,50,"No hay suficientes jugadores para realizar un 11",color=(0,0,0,1),fontsize=20,weight="bold")
    else:
        nomb_jugadores = jugadores['Jugador']
        nomb_jugadores = nomb_jugadores.tolist()

        if formacion == '4-3-3':
            plt.scatter(3,50,300,color=line,zorder=3)
            plt.scatter(30,90,300,color=line,zorder=3)
            plt.scatter(30,10,300,color=line,zorder=3)
            plt.scatter(22,65,300,color=line,zorder=3)
            plt.scatter(22,35,300,color=line,zorder=3)
            plt.scatter(55,75,300,color=line,zorder=3)
            plt.scatter(55,25,300,color=line,zorder=3)
            plt.scatter(45,50,300,color=line,zorder=3)
            plt.scatter(78,15,300,color=line,zorder=3)
            plt.scatter(78,85,300,color=line,zorder=3)
            plt.scatter(80,50,300,color=line,zorder=3)
            
            num_jug1 = plt.text(2.5,49,"1",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug1 = plt.text(6,49,nomb_jugadores[0],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug2 = plt.text(29.5,9,"2",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug2 = plt.text(33,9,nomb_jugadores[1],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug3 = plt.text(29.5,88.5,"3",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug3 = plt.text(33,88.5,nomb_jugadores[2],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug4 = plt.text(21.5,64,"4",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug4 = plt.text(24,64,nomb_jugadores[3],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug5 = plt.text(21.5,34,"5",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug5 = plt.text(24,34,nomb_jugadores[4],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug6 = plt.text(54.2,73.8,"6",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug6 = plt.text(58.2,73.8,nomb_jugadores[5],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug7 = plt.text(54.2,23.8,"7",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug7 = plt.text(58.2,23.8,nomb_jugadores[6],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug8 = plt.text(44.2,48.7,"8",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug8 = plt.text(48.2,48.7,nomb_jugadores[7],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug9 = plt.text(77.2,14,"9",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug9 = plt.text(81.2,14,nomb_jugadores[8],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug10 = plt.text(76.5,84,"10",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug10 = plt.text(80.5,84,nomb_jugadores[9],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug11 = plt.text(78.5,49,"11",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug11 = plt.text(78,54,nomb_jugadores[10],color=(0,0,0,1),fontsize=13,weight="bold")

        elif formacion == '5-4-1':
            plt.scatter(3,50,300,color=line,zorder=3)
            plt.scatter(34,95,300,color=line,zorder=3)
            plt.scatter(34,5,300,color=line,zorder=3)
            plt.scatter(22,74,300,color=line,zorder=3)
            plt.scatter(22,26,300,color=line,zorder=3)
            plt.scatter(20,50,300,color=line,zorder=3)
            plt.scatter(45,65,300,color=line,zorder=3)
            plt.scatter(45,35,300,color=line,zorder=3)
            plt.scatter(55,85,300,color=line,zorder=3)
            plt.scatter(55,15,300,color=line,zorder=3)
            plt.scatter(70,50,300,color=line,zorder=3)
            
            num_jug1 = plt.text(2.2,49,"1",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug1 = plt.text(2.2,54,nomb_jugadores[0],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug2 = plt.text(33.2,3.5,"2",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug2 = plt.text(37.2,3.5,nomb_jugadores[1],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug3 = plt.text(33.2,94,"3",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug3 = plt.text(37.2,94,nomb_jugadores[2],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug4 = plt.text(21.2,72.8,"4",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug4 = plt.text(25.2,72.8,nomb_jugadores[3],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug5 = plt.text(21.2,25,"6",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug5 = plt.text(25.2,25,nomb_jugadores[5],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug6 = plt.text(19.2,48.8,"5",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug6 = plt.text(23.2,48.8,nomb_jugadores[4],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug7 = plt.text(44.5,64,"7",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug7 = plt.text(48.5,64,nomb_jugadores[6],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug8 = plt.text(44.5,34,"8",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug8 = plt.text(48.5,34,nomb_jugadores[7],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug9 = plt.text(54.2,83.75,"9",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug9 = plt.text(58.5,83.75,nomb_jugadores[8],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug10 = plt.text(53.5,13.75,"10",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug10 = plt.text(58.5,13.75,nomb_jugadores[9],color=(0,0,0,1),fontsize=13,weight="bold")

            num_jug11 = plt.text(68.5,49,"11",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug11 = plt.text(72.5,49,nomb_jugadores[10],color=(0,0,0,1),fontsize=13,weight="bold")

        elif formacion == '3-5-2':   
            plt.scatter(3,50,300,color=line,zorder=3)
            plt.scatter(60,95,300,color=line,zorder=3)
            plt.scatter(60,5,300,color=line,zorder=3)
            plt.scatter(26,82,300,color=line,zorder=3)
            plt.scatter(26,18,300,color=line,zorder=3)
            plt.scatter(20,50,300,color=line,zorder=3)
            plt.scatter(45,65,300,color=line,zorder=3)
            plt.scatter(45,35,300,color=line,zorder=3)
            plt.scatter(58,50,300,color=line,zorder=3)
            plt.scatter(75,65,300,color=line,zorder=3)
            plt.scatter(75,35,300,color=line,zorder=3)


            num_jug1 = plt.text(2.2,49,"1",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug1 = plt.text(2.2,54,nomb_jugadores[0],color=(0,0,0,1),fontsize=13,weight="bold")

            num_jug2 = plt.text(59.2,3.5,"2",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug2 = plt.text(63.2,3.5,nomb_jugadores[1],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug3 = plt.text(59.2,93.8,"3",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug3 = plt.text(63.2,93.8,nomb_jugadores[2],color=(0,0,0,1),fontsize=13,weight="bold")

            num_jug4 = plt.text(25.2,80.7,"4",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug4 = plt.text(29.2,80.7,nomb_jugadores[3],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug5 = plt.text(19.2,48.8,"5",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug5 = plt.text(23.2,48.8,nomb_jugadores[4],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug6 = plt.text(25.2,17,"6",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug6 = plt.text(29.2,17,nomb_jugadores[5],color=(0,0,0,1),fontsize=13,weight="bold")


            um_jug7 = plt.text(44.2,33.8,"7",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug7 = plt.text(48.2,33.8,nomb_jugadores[6],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug8 = plt.text(44.2,64,"8",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug8 = plt.text(48.2,64,nomb_jugadores[7],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug9 = plt.text(57.2,48.7,"9",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug9 = plt.text(61.2,48.7,nomb_jugadores[8],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug10 = plt.text(73.5,63.75,"10",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug10 = plt.text(77.5,63.75,nomb_jugadores[9],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug11 = plt.text(73.5,33.75,"11",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug11 = plt.text(77.5,33.75,nomb_jugadores[10],color=(0,0,0,1),fontsize=13,weight="bold")

        else: 
            plt.scatter(3,50,300,color=line,zorder=3)
            plt.scatter(30,90,300,color=line,zorder=3)
            plt.scatter(30,10,300,color=line,zorder=3)
            plt.scatter(22,65,300,color=line,zorder=3)
            plt.scatter(22,35,300,color=line,zorder=3)
            plt.scatter(45,65,300,color=line,zorder=3)
            plt.scatter(45,35,300,color=line,zorder=3)
            plt.scatter(55,85,300,color=line,zorder=3)
            plt.scatter(55,15,300,color=line,zorder=3)
            plt.scatter(75,65,300,color=line,zorder=3)
            plt.scatter(75,35,300,color=line,zorder=3)
            
            num_jug1 = plt.text(2.5,49,"1",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug1 = plt.text(6,49,nomb_jugadores[0],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug2 = plt.text(29.5,9,"2",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug2 = plt.text(33,9,nomb_jugadores[1],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug3 = plt.text(29.5,88.5,"3",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug3 = plt.text(33,88.5,nomb_jugadores[2],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug4 = plt.text(21.5,64,"4",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug4 = plt.text(24,64,nomb_jugadores[3],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug5 = plt.text(21.5,34,"5",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug5 = plt.text(24,34,nomb_jugadores[4],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug6 = plt.text(44.5,64,"6",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug6 = plt.text(47,64,nomb_jugadores[5],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug7 = plt.text(44.5,34,"7",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug7 = plt.text(47,34,nomb_jugadores[6],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug8 = plt.text(54.5,83.75,"8",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug8 = plt.text(57,83.75,nomb_jugadores[7],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug9 = plt.text(54.5,13.75,"9",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug9 = plt.text(57,13.75,nomb_jugadores[8],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug10 = plt.text(74,63.75,"10",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug10 = plt.text(77.5,63.75,nomb_jugadores[9],color=(0,0,0,1),fontsize=13,weight="bold")
            num_jug11 = plt.text(74,33.75,"11",color=(0,0,0,1),fontsize=13,weight="bold")
            text_jug11 = plt.text(77.5,33.75,nomb_jugadores[10],color=(0,0,0,1),fontsize=13,weight="bold")

    # rectangulos
    rec1 = plt.Rectangle((83,21.1), 17, 57.8,ls='-',color=pitch, zorder=1,alpha=1)
    rec2 = plt.Rectangle((0,21.1), 17, 57.8,ls='-',color=pitch, zorder=1,alpha=1)
    rec3 = plt.Rectangle((-1,-1), 102, 102,color=pitch,zorder=1,alpha=1)

    ax.add_artist(rec3)
    ax.add_artist(circle1)
    ax.add_artist(circle2)
    ax.add_artist(rec1)
    ax.add_artist(rec2)
    ax.add_artist(circle3)

    return fig
    
