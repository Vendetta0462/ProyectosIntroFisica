#Función para el análisis de los datos.
#La volvemos a definir en este directorio para poderla importar en el archivo "Péndulo con Ángulo Grande.ipynb"

#Importamos las librerías necesarias
import numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
import pandas as pd

#Definimos la función
def anDatExp (loc, fmt, cic=None, sets=10):
    
    """
    Esta función importa los datos experimentales y los promedia dejando
    como cantidad de datos la cantidad del set con menor cantidad de datos.
    Además, la función siempre genera una grafica, la cual puede ser los
    datos de ángulos promediados con respecto a su tiempo, o, cuando se
    especifican los rangos en los que pueden estar los picos del periodo que
    se desea, se grafica esos puntos dentro de ese rango de tiempo, además,
    se calcula el periodo y la aceleración de gravedad en base a esos puntos
    seleccionados.
    
    Params:
    loc:
        String. Dirección de los archivos a analizar en base a la posición
        del archivo del código.
    fmt:
        String. Formato que tienen los .csv sobre los cuales se va a realizar
        el análisis. Este formato es específico para cada set de datos.
    cic:
        Tupla o array. Los rangos de tiempo en los cuales están los picos del
        ciclo que se desee analizar. Por defecto: None.
    sets:
        Entero. Cantidad de archivos con datos que se va a analizar. Por 
        defecto: 10.
    
    Returns:
        datos_master:
            DataFrame. Contiene los valores del tiempo, el ángulo y la gravedad
            en cada instante de tiempo resultantes del promedio, análisis y
            cálculo.
    """
    
    #Creamos un DF para alojar los valores de los ángulos de todos los sets de datos
    datos_theta = pd.DataFrame()
    
    #Importamos todos los sets (10) de datos y alojamos los valores de los ángulos en
    #el DF creado para ello. Podemos hacer esto debido a que los tiempos de los datos
    #(redondeados a 2 decimales) son iguales para todos los datos. Además, el marco
    #de referencia de tracker no fue configurado, por tanto los angulos salen negativos
    #y con un desfase de 90 grados, así que revertimos esto al importarlos.
    for i in range(1,sets+1):
        globals()["datos_" + str(i)] = pd.read_csv(loc+str(i)+fmt,
                                      skiprows=2,
                                      index_col=False,
                                      sep=".",
                                      names=("t","theta"),
                                      converters={"theta" : lambda x: ((float(x[0:-1].replace(',','.')))+90)*-1,
                                                  "t" : lambda y: (round(float(y.replace(",",".")), ndigits = 2))}
                                      )
        datos_theta["theta_" + str(i)] = globals()["datos_" + str(i)].theta
        
    #Hacemos el promedio horizontal de los datos, para tener un promedio en cada
    #instante de tiempo. Este promedio tiene el mismo número de datos ya que al
    #agragar los valores de los ángulos en el paso anterior, se hace con el
    #número de datos mínimo de todos los sets de datos. Luego alojamos todo en
    #un DF datos_master
    datos_theta_prom = datos_theta.mean(axis=1)
    datos_master = pd.DataFrame()
    datos_master["theta"] = round(datos_theta_prom, ndigits=2)
    datos_master["t"] = datos_1.t

    #Graficamos los ángulos promediados respecto al tiempo de los datos experimentales
    #completos si no se seccionó el ciclo.
    if cic == None:
        plt.figure()
        plt.plot(datos_master.t, datos_master.theta, color="green")
        plt.axhline(0, color="k", alpha=0.5)
        plt.xlabel(r"$Tiempo(s)$", size=13)
        plt.ylabel(r"$\theta(deg)$", size=13)
        plt.xlim([0,datos_master.t.values[-1]])
        plt.title("Posición angular respecto al tiempo ("+fmt[1:-4]+")", size=14, fontstyle="oblique")
        plt.grid(alpha=0.5)
        plt.show()
        return datos_master
    
    #Tomaremos un solo ciclo para hallar el valor del periodo (T) del movimiento.
    #Como se puede ver en los gráficos, el mejor ciclo para hallar T es el segundo,
    #para esto, se ingresa un parámetro en la función que nos indica entre que
    #instantes de tiempo se encuentra este ciclo (y sus picos).
    else:
        datos_cic = datos_master[datos_master.t >= cic[0][0]]
        datos_cic = datos_cic[datos_cic.t <= cic[1][1]]
        picos = np.array([datos_cic[datos_cic.t <= cic[0][1]].theta.max(), datos_cic[datos_cic.t >= cic[1][0]].theta.max()])
        print("Los valores tomados como máximos en el ciclo seleccionado son, respectivamente:", picos)
        lim1 = datos_cic.t[datos_cic.t <= cic[0][1]][datos_cic[datos_cic.t <= cic[0][1]].theta == picos[0]].values[0]
        lim2 = datos_cic.t[datos_cic.t >= cic[1][0]][datos_cic[datos_cic.t >= cic[1][0]].theta == picos[1]].values[0]
        T = round(lim2-lim1, ndigits=1)
        g = (4*(np.pi**2)*int(fmt[-11]))/(T**2)
        datos_master["g"] = np.ones(datos_master.shape[0])*round(g, ndigits=2)
        datos_master["Per"] = np.ones(datos_master.shape[0])*T
        print("El periodo del movimiento es de T=",np.round(T*u.s, decimals=2), sep="")
        print("La gravedad del movimiento es de g=",np.round(g*u.m/u.s**2, decimals=2), sep="")
        
        plt.figure()
        plt.plot(datos_cic.t, datos_cic.theta, color="green")
        plt.axhline(0, color="k", alpha=0.5)
        plt.axvline(lim1, color="r", alpha=0.8)
        plt.axvline(lim2, color="r", alpha=0.8)
        plt.xlabel(r"$Tiempo(s)$", size=13)
        plt.ylabel(r"$\theta(deg)$", size=13)
        plt.xlim([datos_cic.t.values[0],datos_cic.t.values[-1]])
        plt.title("Posición angular respecto al tiempo ("+fmt[1:-4]+")", size=14, fontstyle="oblique")
        plt.grid(alpha=0.5)
        plt.show()
        return datos_master