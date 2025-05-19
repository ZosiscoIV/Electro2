import urequests
import network
import time
import machine
import math
import _thread

class HX711:
    def __init__(self, dout, pd_sck):
        self.dout = machine.Pin(dout, machine.Pin.IN)
        self.pd_sck = machine.Pin(pd_sck, machine.Pin.OUT)
        self.OFFSET = 0
        self.REFERENCE_UNIT = 1
        self.init_hx711()

    def init_hx711(self):
        # Initialisation hardware si besoin
        self.pd_sck.value(0)

    def read_raw_bytes(self):
        # Lecture 24 bits brute depuis HX711
        while self.dout.value() == 1:
            pass  # attendre que le signal soit prêt (dout=0)
        data = bytearray(3)
        for i in range(3):
            val = 0
            for _ in range(8):
                self.pd_sck.value(1)
                val = (val << 1) | self.dout.value()
                self.pd_sck.value(0)
            data[i] = val
        # Gain de 128 bits : on fait un pulse supplémentaire
        self.pd_sck.value(1)
        self.pd_sck.value(0)
        return data

    def convert_from_twos_complement(self, val):
        # Convertir 24-bit twos complement en int signé
        if val & 0x800000:
            val = val - 0x1000000
        return val

    def read_raw_value(self):
        """Lire la valeur brute 24 bits signée (sans offset ni référence)."""
        data = self.read_raw_bytes()
        if data is None:
            print("Failed to read raw bytes.")
            return None
        val = (data[0] << 16) | (data[1] << 8) | data[2]
        signed = self.convert_from_twos_complement(val)
        return signed

    def read_long(self):
        """Lire la valeur corrigée en unités de poids."""
        raw = self.read_raw_value()
        if raw is None:
            print("Failed to read raw value.")
            return None
        weight = (raw - self.OFFSET) / self.REFERENCE_UNIT
        return weight

    def set_offset(self, offset):
        print(f"Setting offset to {offset}")
        self.OFFSET = offset

    def set_reference_unit(self, ref_unit):
        if ref_unit == 0:
            raise ValueError("Reference unit cannot be zero.")
        print(f"Setting reference unit to {ref_unit}")
        self.REFERENCE_UNIT = ref_unit

    def tare(self, times=10):
        print("Taring...")
        readings = []
        for _ in range(times):
            val = self.read_raw_value()
            if val is not None:
                readings.append(val)
            time.sleep_ms(100)
        if readings:
            avg = sum(readings) / len(readings)
            self.set_offset(avg)
            print(f"Tare complete. Offset set to: {avg}")
        else:
            print("Tare failed. No valid readings.")

    def calibrate(self, known_weight_kg, times=10):
        print(f"Calibrating with known weight: {known_weight_kg} kg")
        self.tare(times)
        print("Place the known weight...")
        time.sleep(2)
        readings = []
        for _ in range(times):
            val = self.read_raw_value()
            if val is not None:
                corrected = val - self.OFFSET
                readings.append(corrected)
            time.sleep_ms(100)
        if readings:
            avg = sum(readings) / len(readings)
            ref_unit = avg / known_weight_kg
            self.set_reference_unit(ref_unit)
            print(f"Calibration complete. Reference unit: {ref_unit}")
        else:
            print("Calibration failed. No valid readings.")
            
# 7-Segment Display Pins (common cathode)
SEGMENT_PINS = [27, 26, 22, 21, 20, 19, 18]
# Digit Select Pins
DIGIT_PINS = [2, 3, 4]

# Segments for numbers 0-9
SEGMENT_PATTERNS = [
    0b1111110,  # 0
    0b0110000,  # 1
    0b1101101,  # 2
    0b1111001,  # 3
    0b0110011,  # 4
    0b1011011,  # 5
    0b1011111,  # 6
    0b1110000,  # 7
    0b1111111,  # 8
    0b1111011,  # 9
    0b0000000,  # 10
]

class Display:
    def __init__(self, segment_pins, digit_pins):
        print("Initializing Display")
        # Setup segment pins as outputs
        self.segments = [machine.Pin(pin, machine.Pin.OUT) for pin in segment_pins]
        # Setup digit select pins as outputs
        self.digits = [machine.Pin(pin, machine.Pin.OUT) for pin in digit_pins]
        print("Display Initialized")
        
    def display_digit(self, digit, position):
        """Display a single digit on the 7-segment display."""

        # Turn off all digits
        for d in self.digits:
            d.value(1)

        # Turn on correct segments for the digit
        pattern = SEGMENT_PATTERNS[digit]
        for i, seg in enumerate(self.segments):
            seg.value((pattern >> i) & 1)
        
        # Turn on the correct digit
        self.digits[position].value(0)

    def show_number(self, number):
        """Display a 2-digit number on the 7-segment display."""

        # Ensure number is two digits
        round_number = max(0, min(99, int(number)))

        # Display tens digit
        if (round_number // 10):
            self.display_digit(round_number // 10, 0)
            time.sleep_ms(3)
        else:
            self.display_digit(10, 0)
            time.sleep_ms(3)

        
        # Display ones digit
        self.display_digit(round_number % 10, 1)
        time.sleep_ms(3)

        # Display decimal digit
        self.display_digit(int(round((number - math.floor(number)) * 10)), 2)
        time.sleep_ms(3)

def connect_wifi(ssid,password):
    print("Initialisation du Wi-Fi...")

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print("Tentative de connexion au réseau :", ssid)

    wlan.connect(ssid, password)
    while not wlan.isconnected():
        time.sleep(1)
        print("Échec de la connexion : délai dépassé")

    print("Connecté au Wi-Fi :", wlan.ifconfig())
    return wlan

def check_start_command():
    url = "http://192.168.1.45:3000/api/commande"
    try:
        res = urequests.get(url)
        data = res.json()
        res.close()
        return data.get("start", False), data.get("name", "Test") 
    except Exception as e:
        print("Erreur commande :", e)
        return False, "Test"

def send_weight(name, weight):
    url = "http://192.168.1.45:3000/api/poids"
    payload = {"name": name, "weight": weight}
    try:
        response = urequests.post(url, json=payload)
        print("Données envoyées :", response.text)
        response.close()
    except Exception as e:
        print("Erreur lors de l'envoi :", e)


current_weight = 14.8
def display_loop(display):
    global current_weight
    point = machine.Pin(5, machine.Pin.OUT)
    point.value(1)
    while True:
        display.show_number(current_weight)
        time.sleep(0.01) 

def main():
    global current_weight
    SSID = "Proximus-Home-9F10"
    PASSWORD = "wa439u92kr9uu"
    connect_wifi(SSID, PASSWORD)

    hx = HX711(dout=16, pd_sck=17)
    hx.tare()
    print("pose un objet à calibrer")
    time.sleep(5)
    hx.calibrate(1.4)

    display = Display(SEGMENT_PINS, DIGIT_PINS)

    _thread.start_new_thread(display_loop, (display,))

    point = machine.Pin(5, machine.Pin.OUT)
    point.value(1)

    # Composants d'alarme
    buzzer = machine.Pin(14, machine.Pin.OUT)
    alarm_led = machine.Pin(15, machine.Pin.OUT)

    already_sent = False  # Pour ne pas envoyer deux fois

    while True:
        try:

        # 1. Affiche en continu la valeur sur les afficheurs
            weight = hx.read_long()
            if weight is not None:
                current_weight = round(weight, 1)
            else:
                print("Lecture échouée, conservation du dernier poids")
            # 2. Vérifie s’il y a une nouvelle commande
            should_start, product_name = check_start_command()

            if should_start and not already_sent:
                print("Commande reçue, pesée en cours...")

                send_weight(product_name, current_weight)
                already_sent = True  # On bloque l'envoi suivant
                print(f"Le produit {product_name} est de poids : {current_weight}kg")
                
                # 3. Gestion alarme
                if current_weight > 20:
                    buzzer.on()
                    alarm_led.on()
                    print("ALARM: Weight exceeds 20kg!")
                else:
                    buzzer.off()
                    alarm_led.off()

                # 4. Optionnel : notifier que la commande est traitée
                try:
                    urequests.post("http://192.168.1.45:3000/api/commande/reset", json={"start": False, "name": product_name})
                except Exception as e:
                    print("Erreur lors de la fin de commande :", e)

            elif not should_start:
                # Réinitialiser le flag pour détecter la prochaine commande
                already_sent = False

            time.sleep(2)  # Assez rapide pour l’affichage
        
        except Exception as e:
            print("Erreur boucle principale : ", e)

if __name__ == '__main__':
    main()