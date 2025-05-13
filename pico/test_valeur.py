from machine import Pin
from hx711 import *
import time

hx = hx711(Pin(14), Pin(15))
hx.set_power(hx711.power.pwr_up)
hx.set_gain(hx711.gain.gain_128)

while True:
    hx711.wait_settle(hx711.rate.rate_80)
    val = hx.get_value()
    print("Valeur brute sans poids :", val)
    time.sleep(1)