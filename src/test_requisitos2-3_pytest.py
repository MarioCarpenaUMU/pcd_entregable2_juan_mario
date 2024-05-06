import random
import functools
from math import sqrt
import pytest

# Creando una lista de 12 tuplas, cada una con un timestamp y una temperatura en °C generada aleatoriamente
datos = [
    (f"2024-05-01T12:{i*10:02d}:00", random.randint(10, 35))
    for i in range(12)
]
temperaturas = [temp for _, temp in datos]

class PublicadorTemperaturaInvernadero:
    def __init__(self):
        self._sensores = []

    def alta_sensor(self, sensor):
        if sensor not in self._sensores:
            self._sensores.append(sensor)
        else:
            raise ValueError("Sensor ya registrado.")

    def baja_sensor(self, sensor):
        try:
            self._sensores.remove(sensor)
        except ValueError:
            raise ValueError("Intento de eliminar un sensor que no está registrado.")

    def notificarSensor(self, data):
        if not self._sensores:
            raise RuntimeError("No hay sensores registrados para notificar.")
        for sensor in self._sensores:
            sensor.actualizar_valor_temperatura(data)

class Sensor(PublicadorTemperaturaInvernadero):
    def __init__(self, nombre):
        super().__init__()
        self.nombre_sensor = nombre
        self.valor_temperatura = 0

    def actualizar_valor_temperatura(self, data):
        if not isinstance(data, (int, float)):
            raise ValueError("Datos de temperatura deben ser numéricos.")
        self.valor_temperatura = data
        print(f"{self.nombre_sensor} ha recibido una nueva temperatura: {data} Cº")

#chain of responsability

class Manejador:
    def __init__(self, manejador=None):
        self.manejador = manejador

    def manejar_temperatura(self, temperaturas):
        if not isinstance(temperaturas, list) or not all(isinstance(x, (int, float)) for x in temperaturas):
            raise ValueError("Temperaturas deben ser una lista de números.")
class Estadisticos(Manejador):
    def manejar_temperatura(self,peticion,temperaturas):
        if peticion.level == "Estadisticos":
            temperaturas_60s = temperaturas[0:11]
            media = self.calcularMedia(temperaturas_60s)
            mediana = self.calcularMediana(temperaturas_60s)
            desviacion_tipica = self.calcularDesviacionTipica(temperaturas_60s)
            print(f"La media de la temperatura en los últimos 60 segundos es: {media} Cº, la mediana es: {mediana} Cº y la desviación típica es: {desviacion_tipica} Cº")
        elif self.manejador is not None:
            self.manejador.manejar_temperatura(peticion,temperaturas)
    def calcularMedia(self, lista):
        suma = functools.reduce(lambda t1, t2: t1+t2, lista)
        return suma/len(lista)

    def calcularMediana(self,lista):
        return sorted(lista)[int(len(lista)/2)]

    def DiferenciaAlCuadrado(self,lista):
        m = self.calcularMedia(lista)
        def f(n):
            return (n-m)**2
        return f

    def calcularDesviacionTipica(self,lista):
        suma = sum(map(self.DiferenciaAlCuadrado(lista),lista))
        return sqrt(suma/len(lista))

class Umbral(Manejador):
    def manejar_temperatura(self,peticion,temperaturas):
        if peticion.level == "Umbral":
            supera_umbral = self.superanUmbral(temperaturas[-1])
            print(f"¿La temperatura actual supera el umbral?: {supera_umbral}")
        elif self.manejador is not None:
            self.manejador.manejar_temperatura(peticion,temperaturas)
    def superanUmbral(self,temperatura):
        umbral=36
        return temperatura > umbral

class CrecimientoTemperatura(Manejador):
    def manejar_temperatura(self,peticion,temperaturas):
        if peticion.level == "CrecimientoTemperatura":
            temperaturas_30s = temperaturas[0:5]
            crecimiento= self.comprobar_aumento(temperaturas_30s)
            print(f"¿Se ha producido un aumento de más de 10Cº en los últimos 30 segundos?: {crecimiento}")
        elif self.manejador is not None:
            self.manejador.manejar_temperatura(peticion,temperaturas)    
    def comprobar_aumento(self,temperaturas, aumento=10):
        temperatura_inicial = temperaturas[0]
        temperaturas_filtradas = list(filter(lambda t: t > temperatura_inicial + aumento, temperaturas))
        aumento_significativo = functools.reduce(lambda a, b: a or b, temperaturas_filtradas, False)
        return aumento_significativo
class Peticion():
    def __init__(self,level):
        self.level = level    
def test_alta_baja_sensor():
    publicador = PublicadorTemperaturaInvernadero()
    sensor = Sensor("Sensor de prueba")
    publicador.alta_sensor(sensor)
    assert sensor in publicador._sensores
    publicador.baja_sensor(sensor)
    assert sensor not in publicador._sensores

# Test para la clase Sensor
def test_actualizar_valor_temperatura():
    sensor = Sensor("Sensor de prueba")
    sensor.actualizar_valor_temperatura(25)
    assert sensor.valor_temperatura == 25

# Test para la clase Estadisticos
def test_manejar_temperatura_estadisticos():
    estadisticos = Estadisticos()
    peticion = Peticion("Estadisticos")
    # Mock de la función para evitar la necesidad de implementación completa
    estadisticos.manejar_temperatura(peticion, temperaturas)
    # Agrega aserciones específicas para validar el comportamiento esperado

# Test para la clase Umbral
def test_manejar_temperatura_umbral():
    umbral = Umbral()
    peticion = Peticion("Umbral")
    temperatura_actual = 37  # Umbral definido en 36
    assert umbral.superanUmbral(temperatura_actual) == True

# Test para la clase CrecimientoTemperatura
def test_comprobar_aumento():
    crecimiento = CrecimientoTemperatura()
    assert crecimiento.comprobar_aumento(temperaturas) == True

# Test para comprobar la cadena de responsabilidad
def test_cadena_responsabilidad():
    stats = Estadisticos()
    umbral = Umbral(stats)
    crecimiento = CrecimientoTemperatura(umbral)
    request_1 = Peticion("Estadisticos")
    request_2 = Peticion("Umbral")
    request_3 = Peticion("CrecimientoTemperatura")
    crecimiento.manejar_temperatura(request_1, temperaturas)
    crecimiento.manejar_temperatura(request_2, temperaturas)
    crecimiento.manejar_temperatura(request_3, temperaturas)