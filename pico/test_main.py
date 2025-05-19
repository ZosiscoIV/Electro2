import time
import machine

class HX711:
    def __init__(self, dout, pd_sck, gain=128):
        self.PD_SCK = machine.Pin(pd_sck, machine.Pin.OUT)
        self.DOUT = machine.Pin(dout, machine.Pin.IN)
        
        self.GAIN = 0
        self.OFFSET = 0
        self.REFERENCE_UNIT = 1

        self.set_gain(gain)
        time.sleep_ms(1)

    def convert_from_twos_complement(self, value):
        if value & 0x800000:
            value -= 0x1000000
        return value

    def is_ready(self):
        return self.DOUT.value() == 0

    def set_gain(self, gain):
        if gain == 128:
            self.GAIN = 1
        elif gain == 64:
            self.GAIN = 3
        elif gain == 32:
            self.GAIN = 2
        self.PD_SCK.off()
        self.read_raw_bytes()

    def read_next_bit(self):
        self.PD_SCK.on()
        self.PD_SCK.off()
        return self.DOUT.value()

    def read_next_byte(self):
        byte = 0
        for _ in range(8):
            byte <<= 1
            byte |= self.read_next_bit()
        return byte

    def read_raw_bytes(self):
        while not self.is_ready():
            pass
        first = self.read_next_byte()
        second = self.read_next_byte()
        third = self.read_next_byte()
        for _ in range(self.GAIN):
            self.read_next_bit()
        return [first, second, third]

    def read_raw_value(self):
        bytes_ = self.read_raw_bytes()
        raw = (bytes_[0] << 16) | (bytes_[1] << 8) | bytes_[2]
        return self.convert_from_twos_complement(raw)

    def read_weight(self):
        value = self.read_raw_value()
        return (value - self.OFFSET) / self.REFERENCE_UNIT

    def tare(self, times=10):
        total = 0
        for _ in range(times):
            total += self.read_raw_value()
            time.sleep_ms(100)
        self.OFFSET = total / times
        print("Tare done. Offset =", self.OFFSET)

    def calibrate(self, known_weight_kg, times=10):
        print("Remove weight to tare...")
        time.sleep(5)
        self.tare(times)
        print("Place", known_weight_kg, "kg on the scale...")
        time.sleep(5)
        total = 0
        for _ in range(times):
            total += self.read_raw_value()
            time.sleep_ms(100)
        avg = total / times
        self.REFERENCE_UNIT = (avg - self.OFFSET) / known_weight_kg
        print("Calibration done. Reference unit =", self.REFERENCE_UNIT)

# === MAIN TEST ===

def main():
    hx = HX711(dout=14, pd_sck=15)
    
    # Étape 1 : Tare (sans poids)
    hx.tare()

    # Étape 2 : Calibration (avec poids connu)
    known_weight = 6.0  # kg
    hx.calibrate(known_weight)

    # Étape 3 : Lire le poids
    while True:
        weight = hx.read_weight()
        print("Poids mesuré : {:.2f} kg".format(weight))
        time.sleep(1)

if __name__ == "__main__":
    main()
