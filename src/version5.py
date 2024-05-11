import time, datetime
import random
from abc import ABCMeta, abstractmethod
import random
import functools
from math import sqrt
import pytest


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

        #Al tener el método __crearSensor() queda abierta la posibilidad de que en un futuro se creasen más sensores que pudieran trabajar en conjunto
        #solo habría que conocer de cuantos sensores dispone el usuario. 

        sensor1 = self.__crearSensor()
        sensor1.altaSistema(SistemaGestion())    #dar de alta al sistema como recibidor de la información del sensor  
                                                #Se debería de tener un método que obligase al sensor a comenzar la lectura
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

    def finalizarAnalisisTemperaturas():
        pass    




#Segundo Requisito: Observer

class Sensor:                               #Observable
    def __init__(self):
        self.__sistemas_receptores = []    #Podría implementarse como un diccionario, en el que la clave es el timestamp y el valor es la propia temperatura

    def altaSistema(self, sistema):
        if sistema in self.__sistemas_receptores: raise ValueError('Sistema ya registrado')
        self.__sistemas_receptores.append(sistema)
    
    def bajaSitema(self, sistema):
        if sistema not in self.__sistemas_receptores: raise ValueError('El sistema que pretende dar de baja no está registrado')
        self.__sistemas_receptores.remove(sistema)

    def leerRegistroTemperatura(self):          #Esta función permite 'encender' el sensor de forma que comience a registrar la temperatura y 
        registro = generarRegistroTemperatura() #los registros que vaya obteniendo los debe de notificar a sus sistemas observadores
        self.notificarNuevoRegistro(registro)

    def notificarNuevoRegistro(self, registro):     
        if not self.__sistemas_receptores: raise RuntimeError("No hay sistemas registrados para notificar")
        for sis in self.__sistemas_receptores:
            sis.actualizar(registro)


class SistemaAbstracto(metaclass = ABCMeta):        #AbstractObserver
    @abstractmethod
    def actualizar(registro):
        pass


class CadenaOperaciones:
    def __init__(self):
        self.estrategia = Media()
        self.operacion3 = ComprobacionAumento()
        self.operacion2 = ComprobacionUmbral(self.operacion3)
        self.operacion1 = Estadistico(self.estrategia, self.operacion2)

    def start(self, registros_temperatura):
        """
        Si hay que cambiar la estrategia creo que el lugar idóneo sería este método y más aún esta clase... ahora la pregunta es como debo 
        hacerlo para que se cambie la estrategia durante la propia ejecución, obviamente tendré que usar el método .cambiarEstrategia()
        """
        
        ultimos_registros = registros_temperatura

        #Sabemos que 60 segundos son ingual a 12 registros de temperatura, por lo que nos quedamos solamente con los 12 últimos
        if len(registros_temperatura) > 12: 
            ultimos_registros = registros_temperatura[-12:] 

        self.__cambioEstrategia()
        self.__comenzarPasos(ultimos_registros) 

        #los siguientes métodos los pongo privados para que no losherede la clase Observador (SistemaGestion)
    def __cambioEstrategia(self):
        e = random.randint(0, 2)
        strategy = [Media(), DesviacionTipica(), Mediana()]
        self.operacion1.cambiarEstrategia(strategy[e])

    def __comenzarPasos(self, ultimos_registros):

        self.operacion1.manejar_operacion(ultimos_registros)



class SistemaGestion(SistemaAbstracto, CadenaOperaciones):         #Observer
    def __init__(self):
        self.__registros = []                   #
        CadenaOperaciones.__init__(self)

    def actualizar(self, registro):
        
        fechaYhora = datetime.datetime.fromtimestamp(registro[0])
        fechaYhora = fechaYhora.strftime('%Y-%m-%d %H:%M:%S')
        print(f'{fechaYhora}, Tª: {registro[1]}ºC')
        
        self.__registros.append(registro)       #Una vez que nuestro sistema de gestión es notificado sobre un nuevo registro de temperatura, debemos guardar dicho registro
        self.start(self.__registros)




#Requisito 3: Cadena de responsabilidades


class Handler:
    def __init__(self, sucesor = None):
        self.successor = sucesor

    def manejar_operacion(self, registros):
        pass

    def extraerTemperaturas(self, registros):
        return [r[1] for r in registros]

    def cambiarSucesor(self, registros):
        if self.successor: 
            self.successor.manejar_operacion(registros)


        

class Estadistico(Handler):
    #Esta clase Esatístico, hace de Manejador Concreto en la cadena de responsabilidad y de Contexto en Strategy.
    def __init__(self, estrategia = None ,sucesor=None):
        super().__init__(sucesor)
        self.__estrategia = estrategia

    def cambiarEstrategia(self, nueva_estrategia):
        self.__estrategia = nueva_estrategia

    def manejar_operacion(self, registros):
#################ESTRATEGIA##########################
        lista_temperaturas = self.extraerTemperaturas(registros)
        self.__estrategia.calcular(lista_temperaturas)
#####################################################
        self.cambiarSucesor(registros)

        
        
class ComprobacionUmbral(Handler):

    umbral = 42

    def manejar_operacion(self, registros):
        temperaturas = self.extraerTemperaturas(registros)
        temperatura_actual = temperaturas[-1:]
        if temperatura_actual[0] > ComprobacionUmbral.umbral:
            print(f"La temperatura actual {temperatura_actual[0]}ºC ha superado el umbral establecido de {ComprobacionUmbral.umbral}ºC")
        
        self.cambiarSucesor(registros)


class ComprobacionAumento(Handler):
    def manejar_operacion(self, registros): #Si hay menos registros de los que habría con 30 segundos, pq ha dado tiempo, se calcula igual con lo que haya
        temperaturas_ultimos_30s = self.extraerTemperaturas(registros)
        if len(temperaturas_ultimos_30s) > 6: temperaturas_ultimos_30s = temperaturas_ultimos_30s[-6:]

        self.__comprobar_aumento(temperaturas_ultimos_30s)
        self.cambiarSucesor(registros)


    def __comprobar_aumento(self, temperaturas):
        if len(temperaturas) < 2:return False
        if functools.reduce(lambda a, d: a + d, map(lambda t1, t2: abs(t1 - t2), temperaturas[:-1], temperaturas[1:]), 0) > 10:
            print(f"La temperatura ha aumentado en más de 10 grados en los últimos 30 segundos ")




#Requisito 4: Strategy

class Estrategia(metaclass = ABCMeta):
    @abstractmethod
    def calcular(self, temperaturas):
        pass


class Media(Estrategia):
    def calcular(self, temperaturas):
        suma = functools.reduce(lambda t1, t2: t1+t2, temperaturas)
        print(f'La temperatura media en los últimos 60s es: {round(suma/len(temperaturas),2)}º') 

class Mediana(Estrategia):
    def calcular(self,temperaturas):
        print(f"La mediana de las temperaturas es: {sorted(temperaturas)[int(len(temperaturas)/2)]}º")
    

class DesviacionTipica(Estrategia):
    def calcular(self, temperaturas):
        suma = sum(map(DiferenciaAlCuadrado(temperaturas),temperaturas))
        print(f"La desviación típica es: {round(sqrt(suma/len(temperaturas)))}º")


#función Auxiliar que permite el cálculo de la expresión del numerador de la Desviación Típica.
def DiferenciaAlCuadrado(lista):
    m = functools.reduce(lambda t1, t2: t1+t2, lista)/len(lista)
    def f(n):
        return (n-m)**2
    return f

def test_generar_registro_temperatura():
    timestamp, temperatura = generarRegistroTemperatura()
    assert -15 <= temperatura <= 85, "La temperatura debe estar en el rango de -15 a 85 grados."
    assert isinstance(timestamp, int), "El timestamp debe ser un entero."

def test_singleton_gestor_invernadero():
    gestor1 = GestorInvernadero.obtenerControlInvernadero()
    gestor2 = GestorInvernadero.obtenerControlInvernadero()
    assert gestor1 is gestor2, "Debería devolver siempre la misma instancia."




if __name__ == "__main__":

    invernadero = GestorInvernadero.obtenerControlInvernadero()
    invernadero.comenzarAnalisisTemperaturas(50)

   