import time, datetime
import random
from abc import ABCMeta, abstractmethod
import random
import functools
from math import sqrt
import numpy as np
from itertools import combinations
import pytest



class DepartamentoError(Exception):         
    def __init__(self, mensaje= "Error: Departamento Pasado No válido"):
        self.message = mensaje
        super().__init__(self.message)





class NotValidType(Exception):
    def __init__(self, mensaje="Error: El tipo proporcionado no es válido"):
        self.message = mensaje
        super().__init__(self.message)












#El código a continuación se encuentra ordenado agrupando a las clases según al requisito al que responden


#Esta función nos permite devolver un registro de tiempo y temperatura por cada llamada que se le haga.
#El tiempo corresponde siempre con la fecha y hora actual en formato timestamp,  este es el formato de fecha y hora de 
#Coordinated Universal Time (UTC) en segundos desde el 1 de enero de 1970 a las 00:00:00 (UTC), conocido como "Epoch time" o "Unix time".
#Mientras que la temperatura son valores decimales generados aleatoriamente en un rango de entre -15 y 85 grados. Esto puede dar lugar a que
#se de en periodos de tiempo pequeños una variación muy brusca de temperatura.

def generarRegistroTemperatura():
        """
        Esta función permite generar registros de fecha, hora y temperatura. La temperatura generada es aleatoria
        dentro de un rango de entre -15 y 85 grados. 
        Hemos decidido hacerlo como una función global, ya que emula de forma más fiel a la realidad, ya que el sensor debe 
        'leer' los datos de su entorno.
        """
        timestamp = int(time.time())
        temperatura = round(random.uniform(-15, 85), 1)
        return (timestamp, temperatura)



#Primer Requisito: Singleton

"""Clase GestorInvernadero"""
#Se implementa una clase 'GestorInvernadero' que sigue el patrón de diseño Singleton, lo que nos permite poder tener una 
#sola instancia de su clase, y así proporcionar un único punto de acceso al sistema de gestión del invernadero. 
#Presenta un método 'comenzarAnálisisTemperaturas()', que permite inicial el proceso de análisis de las temperaturas. A este método
#se le puede pasar un parámetro 'duración' indicando cuanto tiempo queremos permitir que dure el análisis. Se puede no establecer duración
#concreta y que el análisis continúe de forma indeterminada.
#Además este método itera cada 5 segundos pidiendo al objeto 'Sensor()' del siguiente requisito que lea registros de tiempo y temperatura. 

class GestorInvernadero:
    _invernadero = None

    @classmethod
    def obtenerControlInvernadero(cls):     
        if not cls._invernadero:
            cls._invernadero = cls()
        return cls._invernadero
    
    
    def __crearSensor(self):
        return Sensor()
    
    def comenzarAnalisisTemperaturas(self, duracion = None):
        if duracion and not isinstance(duracion, int): raise NotValidType

        sensor1 = self.__crearSensor()
        sensor1.altaSistema(SistemaGestion())      
                                                
        if  not duracion:
            while True:
                self.__iteracion(sensor1)
                time.sleep(5)
        else:
            fin = time.time() + duracion
            while fin > time.time():
                self.__iteracion(sensor1)
                time.sleep(5)


    def __iteracion(self, sensor):                      
        sensor.leerRegistroTemperatura()        
        print("\n")





#Segundo Requisito: Observer

"""Clase Sensor"""
#Esta clase 'Sensor()' actúa como la clase 'Observable' del patrón Observer aquí implementado.
#Tiene un método 'leerRegistroTemperatura'  que es llamado desde el Singleton por cada iteración para que 'lea' 
#los datos de temperatura, y los notifique a los 'Sistemas' conectados a él, para que estos últimos puedan trabajar con dichos datos.
#Tiene métodos para añadir y eliminar distintos Sistemas, por lo que es extensible a más Sistemas.
#Presenta también un método que permite notificar a sus sistemas conectados sobre los registros de temperatura y tiempo que 'lee'


class Sensor:                               #Observable
    def __init__(self):
        self.__sistemas_receptores = []    

    def altaSistema(self, sistema):
        if not isinstance(sistema, SistemaAbstracto): raise NotValidType("Error: El sistema proporcionado No es válido")
        if sistema in self.__sistemas_receptores: raise ValueError('Sistema ya registrado')
        self.__sistemas_receptores.append(sistema)
    
    def bajaSitema(self, sistema):
        if not isinstance(sistema, SistemaAbstracto): raise NotValidType("Error: El sistema proporcionado No es válido")
        if sistema not in self.__sistemas_receptores: raise ValueError('El sistema que pretende dar de baja no está registrado')
        self.__sistemas_receptores.remove(sistema)

    def leerRegistroTemperatura(self):          
        registro = generarRegistroTemperatura() 
        self.notificarNuevoRegistro(registro)

    def notificarNuevoRegistro(self, registro):     
        if not self.__sistemas_receptores: raise RuntimeError("No hay sistemas registrados para notificar")
        for sis in self.__sistemas_receptores:
            sis.actualizar(registro)


"""Clase SistemaAbstracto"""
#Se trata de una clase abstracta que fuerza al resto de sistemas, que son observadores concretos en el ámbito del patrón Observer,
#a implementar 'actualizar', ese método de 'recepción' de la información enviada por el Observable

class SistemaAbstracto(metaclass = ABCMeta):        #AbstractObserver
    @abstractmethod
    def actualizar(registro):
        pass


"""Clase CadenaOperaciones"""
#Esta clase queda fuera del ámbito del patrón Observer. Se implemetó como clase auxiliar que permitiese proporcionar por herencia
#al observador (SistemaGestión) un método con el que poder dar comienzo a la ejecución de los pasos del siguiente requisito.
#No se implementa conjuntamente con la clase abstarcta anterior 'SistemaAbstracto' ya que puede que en un futuro se tuvieran que implementar nuevos
#observadores que heredasen de esta última, y llevasen a cabo tareas ajenas a las operaciones que en CadenaOperaciones se inicializan.
#Además al aplicar herencia con esta clase, se permite la instanciación del resto de clases de los requisitos 3 y 4 al mismo momento de 
#instanciar a la clase SistemaGestion. 
#Esto es una gran ventaja en cuanto a recursos del ordenador, ya que permite tener un único objeto de cada clase independientemente de las iteraciones
#del bucle (de la clase Singleton), y no crear un objeto nuevo de cada clase por cada iteración. Ya que el bucle podría durar indefinidamente.
#Cumple también con la tarea de controlar que las operaciones siguientes solo se hagan con los registros de temperatura de los últimos 60 segundos.

class CadenaOperaciones:
    def __init__(self):
        self.__operacion3 = ComprobacionAumento()
        self.__operacion2 = ComprobacionUmbral(self.__operacion3)
        self.__operacion1 = Estadistico(estrategia = None, sucesor=self.__operacion2)

    def  __extraerUltimosResgistros(self, registros):        #Sabemos que 60 segundos son ingual a 12 registros de temperatura, por lo que nos quedamos solamente con los 12 últimos
        if len(registros) > 12: return registros[-12:]
        return registros

    def start(self, registros):
        
        ultimos_registros = self.__extraerUltimosResgistros(registros)
        self.__cambioEstrategia()
        self.__comenzarPasos(ultimos_registros) 

    def __cambioEstrategia(self):
        e = random.randint(0, 3)
        strategy = [MediaDesv(), Mediana(), MaxMin(), Cuantiles()]
        self.__operacion1.cambiarEstrategia(strategy[e])

    def __comenzarPasos(self, ultimos_registros):

        self.__operacion1.manejar_operacion(ultimos_registros)


"""Clase SistemaGestion"""
#
#Esta clase es el único observador del patrón Observer. Presenta herencia múltiple, heredando de la clase abstracta SistemaAbstractae que hace de 
#observador abstarcto y de la clase CadenaOperaciones que permite enlazarla de forma consistente y extensible con las clases de los requisitos siguientes
#que tienen que trabajar con los registros que esta les pase.


class SistemaGestion(SistemaAbstracto, CadenaOperaciones):         #Observer
    def __init__(self):
        self.__registros = []                   
        CadenaOperaciones.__init__(self)

    def actualizar(self, registro):
        
        fechaYhora = datetime.datetime.fromtimestamp(registro[0])
        fechaYhora = fechaYhora.strftime('%Y-%m-%d %H:%M:%S')
        print(f'{fechaYhora}, Tª: {registro[1]}ºC')
        
        self.__registros.append(registro)       
        self.start(self.__registros)





#Requisito 3: Cadena de responsabilidades

"""Clase Handler"""
#Es la clase base de la cadena de responsabilidad. Permite definir los métodos que deban tener los manejadores como clases derivadas.
#Tiene un método que permite extraer las temperaturas de los resgistros de tiempo y temperatura. Pasándo del formato
#[(timestamp, tem),(timestamp, temp),...(timestamp, temp)] al formato [temp, temp, ...,temp]
#También enmascara en un método común a todos los manejadores, el envío de petición al siguiente manejador de la cadena.


class Handler:
    def __init__(self, sucesor = None):
        if sucesor and not isinstance(sucesor, Handler): raise NotValidType('Error: Sucesor No Válido')
        self.sucesor = sucesor

    def manejar_operacion(self, registros):
        pass

    def extraerTemperaturas(self, registros):
        return [r[1] for r in registros]

    def cambiarSucesor(self, registros):
        if self.sucesor: 
            self.sucesor.manejar_operacion(registros)


"""Clase Estadístico"""
#Esta clase nos permite calcular diferentes estadísticos de la temperatura durante los últimos 60 segundos.
#Los estadísticos que calcula requieren de implementaciones distintas que están individualmente recogidas en clases 'estrategia', propias
#del patrón Strategy. Por lo tanto esta clase no solo es un manejador concreto de la cadena de responsabilidad, sino que a la misma vez actúa como 
#contexto del patrón Strategy.
#Tiene un método que permite cambiar de estrategia, propio del patrón contexto. Además a este método se llama por cada iteración desde la clase
#CadenaOperaciones para que se pueda cambiar de forma dinámica la estrategia durante la ejecución.
#El método manejar_operación permite calcular la operación estádistica definida en la estrategia que sea en cada momento.
#Al terminar de realizar su operación, pasa el control a su manejador sucesor (siguiente en la cadena)
        

class Estadistico(Handler):
    def __init__(self, estrategia = None ,sucesor=None):
        super().__init__(sucesor)
        if estrategia and not isinstance(estrategia, Estrategia): raise NotValidType('Error: Estrategia seleccionada No válida')
        self.__estrategia = estrategia

    def cambiarEstrategia(self, nueva_estrategia):
        if not isinstance(nueva_estrategia, Estrategia): raise NotValidType('Error: Estrategia seleccionada No válida')
        self.__estrategia = nueva_estrategia

    def manejar_operacion(self, registros):
        lista_temperaturas = self.extraerTemperaturas(registros)
        self.__estrategia.calcular(lista_temperaturas)
        self.cambiarSucesor(registros)

        
"""Clase ComprobacionUmbral"""
#Esta clase es otro manejador de la cadena de responsabilidad. Define arbitrariamente un valor de umbral como atributo de clase, 
#que se emplea para comparar el valor de la temepratura actual y poder determinar si se supera.

class ComprobacionUmbral(Handler):

    __umbral = 42

    def manejar_operacion(self, registros):
        temperaturas = self.extraerTemperaturas(registros)
        temperatura_actual = temperaturas[-1:]
        if temperatura_actual[0] > ComprobacionUmbral.__umbral:
            print(f"La temperatura actual {temperatura_actual[0]}ºC ha superado el umbral establecido de {ComprobacionUmbral.__umbral}ºC")
        
        self.cambiarSucesor(registros)


"""Clase ComprobacionAumento"""
#Esta clase define al último manejador de la cadena de Responsabilidad. Se encarga de comprobar que en los últimos 30 últimos segundos no haya
#un aumento de temperatura superior a 10 grados.



class ComprobacionAumento(Handler):
    def manejar_operacion(self, registros): #Si hay menos registros de los que habría con 30 segundos, pq ha dado tiempo, se calcula igual con lo que haya
        temperaturas_ultimos_30s = self.extraerTemperaturas(registros)
        if len(temperaturas_ultimos_30s) > 6: temperaturas_ultimos_30s = temperaturas_ultimos_30s[-6:]
        self.__comprobar_aumento(temperaturas_ultimos_30s)
        self.cambiarSucesor(registros)

    def __comprobar_aumento(self, temperaturas):
        if len(temperaturas) < 2:return False
        if sum(map(lambda t1, t2: abs(t2 - t1), temperaturas[:-1], temperaturas[1:])) > 10:
            print(f"La temperatura ha aumentado en más de 10 grados en los últimos 30 segundos ")
 





#Requisito 4: Strategy


"""Clase Estrategia"""
#Es una clase Abstracta que fuerza a la implementación por parte de sus clases derivadas del método común 'calcular()'


class Estrategia(metaclass = ABCMeta):
    @abstractmethod
    def calcular(self, temperaturas):
        pass

"""Clase MediaDesv"""
#Clase que implementa el código necesario para poder sacr la media y la desviación típica de las tenperaturas pasadas.


class MediaDesv(Estrategia):
    def calcular(self, temperaturas):
        media = functools.reduce(lambda t1, t2: t1+t2, temperaturas)/len(temperaturas)
        desv = sum(map(lambda x: (x-media)**2 ,temperaturas))/len(temperaturas)
        print('Últimos 60 segundos')
        print(f'Temp. media: {round(media,2)}º | Desviación típica: {round(sqrt(desv),2)}º') 

"""Clase Mediana"""
#Permite calcular la mediana de las temperaturas pasadas

class Mediana(Estrategia):
    def calcular(self,temperaturas):
        print(f"La mediana de las temperaturas es: {sorted(temperaturas)[int(len(temperaturas)/2)]}º")


"""Clase MaxMin"""
#Permite sacar la temperatura máxima y mínima de entre todas las pasadas
    
class MaxMin(Estrategia):
    def calcular(self, temperaturas):
        print(f"Máx:{max(temperaturas)}º, Min:{min(temperaturas)}º")

"""Clase Cuantiles"""
#Permite calcular los cuantiles (25%, 50%, 75%) de las temperaturas pasadas

class Cuantiles(Estrategia):
    def calcular(self, temperaturas):
        temp = sorted(temperaturas)
        indices = list(map(lambda x: x*(len(temperaturas)-1), [0.25, 0.50, 0.75]))
        percentiles = [temp[int(i)] for i in indices]
        print(f"Cuantiles:\n 25%: {percentiles[0]}º   50%: {percentiles[1]}º    75%: {percentiles[2]}º ")




#TESTS

def test_generar_registro_temperatura():
    try:
        timestamp, temperatura = generarRegistroTemperatura()
        valid_timestamp = isinstance(timestamp, int)
        valid_temperature = isinstance(temperatura, float) and -15 <= temperatura <= 85
        assert valid_timestamp and valid_temperature, "Generación de registro fallida o fuera de rango."
    except Exception as e:
        pytest.fail(f"Error al generar registro: {e}")

def test_singleton_gestor_invernadero():
    try:
        gestor1 = GestorInvernadero.obtenerControlInvernadero()
        gestor2 = GestorInvernadero.obtenerControlInvernadero()
        assert gestor1 is gestor2, "Singleton no mantiene una única instancia."
    except Exception as e:
        pytest.fail(f"Error en Singleton: {e}")

def test_media_desv():
    estrategia = MediaDesv()
    temperaturas = [25, 30, 28, 22, 24]
    try:
        estrategia.calcular(temperaturas)
    except Exception as e:
        pytest.fail(f"Error al calcular media y desviación: {e}")

def test_mediana():
    estrategia = Mediana()
    temperaturas = [10, 20, 30, 40, 50]
    try:
        estrategia.calcular(temperaturas)
    except Exception as e:
        pytest.fail(f"Error al calcular la mediana: {e}")

def test_max_min():
    estrategia = MaxMin()
    temperaturas = [10, 20, 30, 40, 50]
    try:
        estrategia.calcular(temperaturas)
    except Exception as e:
        pytest.fail(f"Error al calcular máximos y mínimos: {e}")

def test_cuantiles():
    estrategia = Cuantiles()
    temperaturas = [10, 20, 30, 40, 50]
    try:
        estrategia.calcular(temperaturas)
    except Exception as e:
        pytest.fail(f"Error al calcular cuantiles: {e}")


if __name__ == "__main__":

    try:
        invernadero = GestorInvernadero.obtenerControlInvernadero()
        invernadero.comenzarAnalisisTemperaturas(120)

    except NotValidType as mensaje:
        print(mensaje)
        raise 
    except ValueError as mensaje:
        print(mensaje)
        raise 
    except RuntimeError as mensaje:
        print(mensaje)
        raise 
        

 