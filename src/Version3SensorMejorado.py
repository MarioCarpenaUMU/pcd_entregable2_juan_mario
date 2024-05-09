import time, datetime
import random
from abc import ABCMeta, abstractmethod
import random
import functools
from math import sqrt



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

    def leerRegistroTemperatura(self):          #Esta función permite 'encender' el sensor de forma que comience a registrar la temperatura y la 
        registro = generarRegistroTemperatura()
        self.notificarNuevoRegistro(registro)

    def notificarNuevoRegistro(self, registro):     
        if not self.__sistemas_receptores: raise RuntimeError("No hay sistemas registrados para notificar")
        for sis in self.__sistemas_receptores:
            sis.actualizar(registro)


class SistemaAbstracto(metaclass = ABCMeta):        #AbstractObserver
    @abstractmethod
    def actualizar(registro):
        pass

class SistemaGestion(SistemaAbstracto):         #Observer
    def __init__(self):
        self.__registros = []

    def actualizar(self, registro):
        
        fechaYhora = datetime.datetime.fromtimestamp(registro[0])
        fechaYhora = fechaYhora.strftime('%Y-%m-%d %H:%M:%S')
        print(f'{fechaYhora}, Tª: {registro[1]}º')
        
        self.__registros.append(registro)       #Una vez que nuestro sistema de gestión es notificado sobre un nuevo registro de temperatura, debemos guardar dicho registro
        CadenaOperaciones.start(self.__registros)




#Requisito 3: Cadena de responsabilidades

class CadenaOperaciones:       #la cadena de sucesos debe ser presentar métodos de clase, no debe instanciarse
    @classmethod
    def start(cls, registros_temperatura):
        if len(registros_temperatura) > 12: 
            ultimos_registros = registros_temperatura[-12:]
        else: 
            ultimos_registros = registros_temperatura

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
    contador = 0
    #Esta clase Esatístico, hace de Manejador Concreto en la cadena de responsabilidad y de Contexto en Strategy.
    def __init__(self, estrategia = None ,sucesor=None):
        super().__init__(sucesor)
        self.__estrategia = estrategia
        Estadistico.contador += 1

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

    print("Número de instancias creadas:", Estadistico.contador)
    
  