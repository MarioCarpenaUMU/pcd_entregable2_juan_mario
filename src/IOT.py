import time, datetime
import random
from abc import ABCMeta, abstractmethod
import random
import functools
from math import sqrt

#Puede que la función inmediata a continuación deba ir en el sigleton...
#Función que me permite sacar una tupla de temperatura cada vez que se le llama.
#la tupla de temperatura presenta la siguiente estructura (timestamp, temperatura)

# def generarRegistroTemperatura(): 
#     timestamp = int(time.time())                    #Esta función time de la librería time permite sacar el timestamp desde el ecpoch hasta la hora actual
#     temperatura = round(random.uniform(-25, 95), 1) #La temperatura es generada de forma aleatoria por lo que puede darse perfectamente el caso de que 
#     return (timestamp, temperatura)                 #ocurran cambios bruscos de temperatura.

#Primer Requisito: Singleton

class GestorInvernadero:
    _invernadero = None

    @classmethod
    def obtenerControlInvernadero(cls):     #Esta es la función que permite obtener la instancia, lo que pasa es que no la iba a nombrar de forma genérica
        if not cls._invernadero:
            cls._invernadero = cls()
        return cls._invernadero
    
    def __leerRegistroTemperatura(self):
        timestamp = int(time.time())
        temperatura = round(random.uniform(-15, 85), 1)
        return (timestamp, temperatura)
    
    def comenzarAnalisisTemperaturas(self, duracion = None):

        sensor1 = Sensor()
        sensor1.altaSistema(SistemaGestion())       #Creo el sensor y el sistema de gestión al que notifica en el propio método que da comienzo 

        #Puede que este sea el sitio correcto donde crear los manejadores Estadistico, CompribacionUmbral y ComprobacionAumento
        #así como las distintas estrategias, ya que el contexto en sí es la clase Esatdístico


        if  not duracion:
            while True:
                self.__iteracion(sensor1)
                time.sleep(5)
        else:
            inicio = time.time()
            fin = inicio + duracion
            while fin > inicio:
                self.__iteracion(sensor1)
                time.sleep(5)


    def __iteracion(self, sensor):                      #Creo un método aparte que permita llevar a cabo cada iteración

        resgistro = self.__leerRegistroTemperatura()
        sensor.notificarNuevoRegistro(resgistro)        #El sensor notifica de un nuevo registro a todos los sistemas a que tengan que leer sus datos
        print("\n")

    def finalizarAnalisisTemperaturas():
        pass    




#Segundo Requisito: Observer

class Sensor:
    def __init__(self):
        self.__sistemas_receptores = []    #Podría implementarse como un diccionario, en el que la clave es el timestampo y el valor es la propia temperatura

    def altaSistema(self, sistema):
        if sistema in self.__sistemas_receptores: raise ValueError('Sistema ya registrado')
        self.__sistemas_receptores.append(sistema)
    
    def bajaSitema(self, sistema):
        if sistema not in self.__sistemas_receptores: raise ValueError('El sistema que pretende dar de baja no está registrado')
        self.__sistemas_receptores.remove(sistema)
    
    def notificarNuevoRegistro(self, registro):     #Donde registro es la tupla (timestamp, temperatura)
        if not self.__sistemas_receptores: raise RuntimeError("No hay sistemas registrados para notificar")
        for sis in self.__sistemas_receptores:
            sis.actualizar(registro)


class SistemaAbstracto(metaclass = ABCMeta):
    @abstractmethod
    def actualizar(registro):
        pass

class SistemaGestion(SistemaAbstracto):
    def __init__(self):
        self.__registros = []

    def actualizar(self, registro):
        
        fechaYhora = datetime.datetime.fromtimestamp(registro[0])
        fechaYhora = fechaYhora.strftime('%Y-%m-%d %H:%M:%S')
        print(f'{fechaYhora}, Tª: {registro[1]}')
        
        self.__registros.append(registro)       #Una vez que nuestro sistema de gestión es notificado de un nuevo registro de temperatura, debemos guardar dicho registro
        CadenaOperaciones.start(self.__registros)








#Requisito 3: Cadena de responsabilidades

class CadenaOperaciones:       #la cadena de sucesos debe ser presentar métodos de clase, no debe instanciarse
    @classmethod
    def start(cls, registros_temperatuta):
        if len(registros_temperatuta) > 12: 
            ultimos_registros = registros_temperatuta[-12:]
        else: 
            ultimos_registros = registros_temperatuta

        paso_inicial = cls.__instanciarPasosCadena()
        paso_inicial.manejar_operacion(ultimos_registros)
        
    
    @classmethod
    def __instanciarPasosCadena(cls):
        estrategia = Media()
        
        paso3 = ComprobacionAumento()
        paso2 = ComprobacionUmbral(paso3)
        paso1 = Estadistico(estrategia, paso2)


        return paso1

        



class Handler:
    def __init__(self, sucesor = None):
        self.successor = sucesor

    def manejar_operacion(self, registros):
        pass

class Estadistico(Handler):
    #Esta clase Esatístico, hace de Manejador Concreto en la cadena de responsabilidad y de Contexto en Strategy.
    def __init__(self, estrategia = None ,sucesor=None):
        super().__init__(sucesor)
        self.__estrategia = estrategia

    def cambiar_estrategia(self, nueva_estrategia):
        self.__estrategia = nueva_estrategia

    def manejar_operacion(self, registros):
#################ESTRATEGIA##########################
        lista_temperaturas = [r[1] for r in registros]
        self.__estrategia.calcular(lista_temperaturas)
#####################################################
        if self.successor:
            self.successor.manejar_operacion(lista_temperaturas)
        
        
class ComprobacionUmbral(Handler):

    umbral = 42

    def manejar_operacion(self, registros):
        temperatura_actual = registros[-1:]
        if temperatura_actual[0] > ComprobacionUmbral.umbral:
            print(f"La temperatura actual {temperatura_actual[0]} ha superado el umbral establecido de {ComprobacionUmbral.umbral}")
        
        if self.successor: 
            self.successor.manejar_operacion(registros)


class ComprobacionAumento(Handler):
    def manejar_operacion(self, registros): #Si hay menos registros de los que habría con 30 segundos, pq ha dado tiempo, se calcula igual con lo que haya
            registros_temperaturas_30s = registros
            if len(registros) > 6: registros_temperaturas_30s = registros[-6:]
            crecimiento= self.comprobar_aumento(registros_temperaturas_30s)
            print(f"¿Se ha producido un aumento de más de 10Cº en los últimos 30 segundos?: {crecimiento}")

            if self.successor:
                self.successor.manejar_operacion(registros)


    def comprobar_aumento(self, temperaturas, aumento=10):
        if len(temperaturas) < 2:
            return False
        solo_temperaturas = [temp for temp in temperaturas]
        temperatura_inicial = solo_temperaturas[0]
        temperaturas_filtradas = list(filter(lambda temp: temp >= temperatura_inicial + aumento, solo_temperaturas))
        aumento_significativo = len(temperaturas_filtradas) > 0

        return aumento_significativo

        


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
        print(f"La mediana de las temperaturas es: {sorted(temperaturas)[int(len(temperaturas)/2)]}")
    

class DesviacionTipica(Estrategia):
    def calcular(self, temperaturas):
        suma = sum(map(DiferenciaAlCuadrado(temperaturas),temperaturas))
        return sqrt(suma/len(temperaturas))


#función Auxiliar que permite el cálculo de la expresión del numerador de la Desviación Típica.
def DiferenciaAlCuadrado(lista):
    m = functools.reduce(lambda t1, t2: t1+t2, lista)/len(lista)
    def f(n):
        return (n-m)**2
    return f

def test_singleton_instance():
    gestor_invernadero = GestorInvernadero.obtenerControlInvernadero()
    assert gestor_invernadero is GestorInvernadero.obtenerControlInvernadero()

def test_temperature_reading():
    gestor_invernadero = GestorInvernadero.obtenerControlInvernadero()
    timestamp, temperature = gestor_invernadero._GestorInvernadero__leerRegistroTemperatura()
    assert isinstance(timestamp, int)
    assert isinstance(temperature, float)
    assert -15 <= temperature <= 85


def test_temperature_increase_detection():
    comprobacion_aumento = ComprobacionAumento()
    temperatures = [20, 30, 35, 45]

    assert comprobacion_aumento.comprobar_aumento(temperatures, aumento=10)
    assert comprobacion_aumento.comprobar_aumento(temperatures, aumento=15) 

if __name__ == "__main__":

    invernadero = GestorInvernadero.obtenerControlInvernadero()
    invernadero.comenzarAnalisisTemperaturas()
    

    
  