from machine import Pin
from hx711 import *
import time

# À modifier pour chaque cellule de charge:
zero = 49000 # soustraire cette valeur pour ajuster le zéro
conversion = 380.0 # diviser par cette valeur pour convertir en grammes

hx = hx711(Pin(14), Pin(15))  # clock broche GP14, data broche GP15
hx.set_power(hx711.power.pwr_up)
hx.set_gain(hx711.gain.gain_128) # valeurs possibles 128, 64 ou 32.

while True:
    hx711.wait_settle(hx711.rate.rate_80)  # on attend qu'une mesure soit prête
    valeur =  hx.get_value() # on prend la mesure
    valeur = (valeur - zero) / conversion  # conversion en grammes   
    print('masse: ' , round(valeur), 'g') 