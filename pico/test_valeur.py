from machine import Pin
from hx711 import *
import time

hx = hx711(Pin(14), Pin(15))
hx.set_power(hx711.power.pwr_up)
hx.set_gain(hx711.gain.gain_128)
hx.set_power(hx711.power.pwr_down)
hx711.wait_power_down()
hx.set_power(hx711.power.pwr_up)
hx711.wait_settle(hx711.rate.rate_80)

# Tare : valeur brute à vide
zero = hx.get_value()
print("TARE / ZERO =", zero)

time.sleep(5)  # Attends 5s pour placer un poids

valeur = hx.get_value()
print("VALEUR AVEC POIDS =", valeur)

poids_grammes = 6000  # poids exact que tu as posé

conversion = (valeur - zero) / poids_grammes
print("VALEUR DE CONVERSION =", conversion)