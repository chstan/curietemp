import visa
from math import sqrt
from tempandres import temperature_from_voltage, temperature_from_resistance

rm = visa.ResourceManager()

class KeithelySourcemeter(object):
    """Class for the Keithley 2400 Sourcemeter"""
    def __init__(self, address, resourceManager, name):
        self.name = name
        self.address = address
        self.device = resourceManager.get_instrument(address)

        self.device.write("*RST")
        self.device.write("*CLS")
        self.device.write(":SYST:LFR:AUTO ON")
        self.device.write(":SYST:RSEN OFF")
        self.device.write(":SOUR:FUNC VOLT")
        self.device.write(":SOUR:VOLT:MODE FIXED")
        self.device.write(":SOUR:VOLT:RANG 20")
        self.set_voltage(0)
        self.device.write(':SENS:FUNC "CURR"')
        self.device.write(':FORM:ELEM CURR')
        self.set_compliance_current(100)

    def output(self, on):
        if on:
            self.device.write(":OUTP ON")
        else:
            self.device.write(":OUTP OFF")

    def read(self):
        data = self.device.write(":READ?")
        print(data)
        return data

    def set_voltage(self, V):
        self.device.write(":SOUR:VOLT:LEV {voltage}".format(voltage = V))
    
    def set_compliance_current(self, milliamps):
        self.device.write(":SENS:CURR:PROT {amperage}E-3".format(amperage = milliamps))
        self.device.write(":SENS:CURR:RANG {amperage}E-3".format(amperage = milliamps))

class Heater(object):
    def __init__(self, sourceMeter, resistance):
        self.resistance = resistance
        self.sourceMeter = sourceMeter

    def off(self):
        self.sourceMeter.output(False)

    def on(self):
        self.sourceMeter.output(True)

    def power(self, P):
        """Sets the power in Watts, does not turn on the heater if not already on"""
        self.sourceMeter.set_voltage(sqrt(P*self.resistance))


class HPMultimeter(object):
    """Class for the HP 34401A Multimeter"""
    def __init__(self, address, resourceManager, name):
        self.name = name
        self.address = address
        self.device = resourceManager.get_instrument(address)
        self.device.write("*RST")
        self.device.write("*CLS")
        self.device.write("SAMP:COUN 100")

    def measure_voltage(self):
        reply = self.device.ask_for_values("MEAS:VOLT:DC?")
        return reply[0]

    def measure_voltage_AC(self):
        reply = self.device.ask_for_values("MEAS:VOLT:AC?")
        return reply[0]

    def measure_resistance(self):
        reply = self.device.ask_for_values("MEAS:FRES?")
        return reply[0]

class KeithleyMultimeter(object):
    def __init__(self, mode, address, resourceManager, name):
        self.mode = mode
        self.name = name
        self.address = address
        self.device = resourceManager.get_instrument(address)

    def voltage_RMS(self):
        assert(self.mode == "AC")
        unproc_voltage = self.device.read()
        return float(unproc_voltage[4:])

    def voltage_P(self):
        return self.voltage_RMS()*sqrt(2)

    def voltage_PP(self):
        return self.voltage_RMS()*2*sqrt(2)

    def voltage_DC(self):
        assert(self.mode == "DC")
        return 0

    def get_mode(self):
        return self.mode

class SRLockin(object):
    """Class for the SR 830 Lock-in Amplifier"""
    def __init__(self, address, resourceManager, name):
        self.address = address
        self.name = name
        self.device = resourceManager.get_instrument(address)
        self.device.write("*CLS")
        self.device.write("FMOD 0")

    def set_time_constant(self, i):
        self.device.write("OFLT {val}".format(val = i))

    def auto_phase(self):
        self.device.write("APHS")

    def auto_gain(self):
        self.device.write("AGAN")

    def read(self):
        return self.device.ask_for_values("SNAP ? 3, 4")

class AgilentFunctionGenerator(object):
    def __init__(self, address, resourceManager, name):
        self.address = address
        self.device = resourceManager.get_instrument(address)
        self.frequency = None
        self.shape = None
        self.amplitude = None
        self.name = name
        self.offset = None
        self.device.write("*CLS")

    def apply(self, shape = "SIN", freq = (2, "KHZ",), amplitude = 0, offset = 0):
        apply_string = "APPL:{a} {fa} {fb}, {c}, {d}".format(a = shape, fa = freq[0], \
                                                    fb = freq[1], c = amplitude, d = offset)
        self.device.write(apply_string)

    def apply_settings(self):
        if (self.shape != None and self.frequency \
            != None and self.amplitude != None and self.offset != None):
            self.apply(self.shape, self.frequency, self.amplitude, self.offset)
        else:
            print("{inst_name} NOT INITIALIZED".format(inst_name = self.name))

    def set_frequency(self, f, reset = True):
        self.frequency = f
        if(reset):
            self.apply_settings()

    def set_shape(self, shape, reset = True):
        self.shape = shape
        if(reset):
            self.apply_settings()

    def set_amplitude(self, amplitude, reset = True):
        self.amplitude = amplitude
        if(reset):
            self.apply_settings()

    def set_offset(self, offset, reset = True):
        self.offset = offset
        if(reset):
            self.apply_settings()

    def set_name(self, name):
        self.name = name
        if(reset):
            self.apply_settings()



class Thermometer(object):
    def __init__(self, multimeter, name):
        self.name = name
        self.multimeter = multimeter

    def temperature(self):
        V = self.multimeter.measure_voltage()
        return temperature_from_voltage(V)

class ResistanceThermometer(object):
    def __init__(self, multimeter, name):
        self.name = name
        self.multimeter = multimeter

    def temperature(self):
        R = self.multimeter.measure_resistance()
        return temperature_from_resistance(R)
