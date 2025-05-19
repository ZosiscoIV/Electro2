from machine import Pin
from hx711 import *
import time

# Initialisation HX711
hx = hx711(Pin(14), Pin(15))
hx.set_power(hx711.power.pwr_up)
hx.set_gain(hx711.gain.gain_128)
hx.set_power(hx711.power.pwr_down)
hx711.wait_power_down()
hx.set_power(hx711.power.pwr_up)
hx711.wait_settle(hx711.rate.rate_80)

# 💡 Calibration
zero = 1572863
conversion = -262.144

# Moyenne de plusieurs mesures
def lire_poids(n=5):
    valeurs = []
    for _ in range(n):
        if val := hx.get_value_timeout(250000):
            valeurs.append(val)
        time.sleep(0.05)
    if valeurs:
        moyenne = sum(valeurs) / len(valeurs)
        poids = (moyenne - zero) / conversion
        return round(poids, 1)
    else:
        return None

# Boucle principale
while True:
    poids = lire_poids()
    if poids is not None:
        print("Poids:", poids, "g")
    else:
        print("Lecture échouée")
    time.sleep(1)