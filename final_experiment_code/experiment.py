import sys, os
import cPickle as pickle
from datetime import datetime
import time

import visa

import instruments
import pid


heater = None
drive_FG = None
thermometer = None
rm = None
source_meter = None
therm_multimeter = None
drive_multimeter = None
lock_in = None

data = []

drive_resistor = 98.8

def setupExperiment():
    global rm
    global source_meter
    global heater
    global drive_FG
    global therm_multimeter
    global thermometer
    global drive_multimeter
    global lock_in
    
    rm = visa.ResourceManager()
    therm_multimeter = instruments.HPMultimeter("GPIB0::1::INSTR", rm, "therm_multimeter")
    drive_multimeter = instruments.HPMultimeter("GPIB0::2::INSTR", rm, "drive_multimeter")
    drive_FG = instruments.AgilentFunctionGenerator("GPIB0::3::INSTR", rm, "drive_FG")
    source_meter = instruments.KeithelySourcemeter("GPIB0::4::INSTR", rm, "source_meter")

    lock_in = instruments.SRLockin("GPIB0::5::INSTR", rm, "lock_in")
    lock_in.set_time_constant(9) # set the time constant to 300ms (8 = 100ms etc)

    drive_FG.set_shape("SIN", False)
    drive_FG.set_amplitude(1, False) # voltages are peak to peak
    drive_FG.set_offset(0, False)
    drive_FG.set_frequency((2, "KHZ"), False)
    drive_FG.apply_settings()

    lock_in.auto_phase()
    time.sleep(5)
    lock_in.auto_gain()
    time.sleep(5)

    heater = instruments.Heater(source_meter, 90)
    thermometer = instruments.Thermometer(therm_multimeter, "thermometer")

def letsGetThisOverWith():
    setupExperiment()
    heater.power(1)
    heater.on()
    while True:
        print thermometer.temperature()

def finishExperiment():
    # turn off the Keithley 2400 Sourcemeter for safety reasons
    heater.off()
    

def collectDataPoint():
    T = thermometer.temperature() # overall phase was 39.08
    drive_FG.set_frequency((1, "KHZ",))
    V_drive_1 = drive_multimeter.measure_voltage_AC()
    lock_in.auto_gain()
    time.sleep(10)
    lock_in_vals_1 = lock_in.read()
    T2 = thermometer.temperature()
    drive_FG.set_frequency((2, "KHZ",))
    V_drive_2 = drive_multimeter.measure_voltage_AC()
    lock_in.auto_gain()
    time.sleep(10)
    lock_in_vals_2 = lock_in.read()
    T3 = thermometer.temperature()
    drive_FG.set_frequency((4, "KHZ",))
    V_drive_4 = drive_multimeter.measure_voltage_AC()
    lock_in.auto_gain()
    time.sleep(10)
    lock_in_vals_4 = lock_in.read()
    T4 = thermometer.temperature()
    drive_FG.set_frequency((8, "KHZ",))
    V_drive_8 = drive_multimeter.measure_voltage_AC()
    lock_in.auto_gain()
    time.sleep(10)
    lock_in_vals_8 = lock_in.read()
    T5 = thermometer.temperature()
    drive_FG.set_frequency((2, "KHZ",))
    print "Recorded temperature range ", T, T2, T3, T4, T5
    return {"Temperature1": T, "Temperature2": T2, "Temperature3": T3, "Temperature4": T4, "Temperature5": T5, \
            "Drive Current RMS1": V_drive_1/drive_resistor, "R1": lock_in_vals_1[0], "Theta1": lock_in_vals_1[1], \
            "Drive Current RMS2": V_drive_2/drive_resistor, "R2": lock_in_vals_2[0], "Theta2": lock_in_vals_2[1], \
            "Drive Current RMS4": V_drive_4/drive_resistor, "R4": lock_in_vals_4[0], "Theta4": lock_in_vals_4[1], \
            "Drive Current RMS8": V_drive_8/drive_resistor, "R8": lock_in_vals_8[0], "Theta8": lock_in_vals_8[1]}

def dec_range(start, stop, step):
    r = start
    while r <= stop:
        yield r
        r += step

def record_temp_file(dir, index):
    file_path = os.path.join(dir, "INCOMPLETEDATA_{i}".format(i=index))
    pickle.dump(data, open(file_path, 'wb+'))

def temperature():
    setupExperiment()
    while True:
        print thermometer.temperature()

def clamp(p, c):
    if p > c:
        return c
    if p < 0:
        return 0
    return p

def testHeater():
    epsilon = 0.05
    setupExperiment()
    heater.power(0)
    heater.on()
    pid_controller = pid.PIDController(0.09*0.1, 0.002*0.1, 0.2*0.05)
    pid_controller.soft_reset()
    for target_temp in range(305, 310):
        print "Adjusting temp to {t}".format(t=target_temp)
        pid_controller.time_reset()
        measured_temp = thermometer.temperature()
        while measured_temp < target_temp:
            measured_temp = thermometer.temperature()
            pid_output = pid_controller.update(measured_temp, target_temp)
            heater.power(clamp(pid_output,0.4))
            print measured_temp, clamp(pid_output, 0.4)
            time.sleep(0.5)


        for i in range(60):
            measured_temp = thermometer.temperature()
            pid_output = pid_controller.update(measured_temp, target_temp)
            heater.power(clamp(pid_output,0.4))
            time.sleep(0.5)
            print measured_temp

        avg_iters = 40
        phold = 0
        for i in range(avg_iters):
            measured_temp = thermometer.temperature()
            pid_output = pid_controller.update(measured_temp, target_temp)
            heater.power(clamp(pid_output,0.4))
            phold += clamp(pid_output, 0.4)
            time.sleep(0.5)
            print measured_temp    
        phold = phold/avg_iters;
        
        heater.power(phold)
        for i in range(10):
            print thermometer.temperature()
            time.sleep(1)
            
    heater.off()

def runExperiment(start_temp, end_temp, temp_res, base_directory):
    
    setupExperiment()

    start_time = datetime.now()

    inter_directory = os.path.join(base_directory, "TEMP")
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)

    if not os.path.exists(inter_directory):
        os.makedirs(inter_directory)

    index = 1
    heater.power(0)
    heater.on()
    beta = 1
    pid_controller = pid.PIDController(0.09*beta, 0.002*beta, 0.2*beta)
    pid_controller.soft_reset()

    measured_temp = thermometer.temperature()

    print "Preheating..."
    while abs(measured_temp - start_temp) > 1.5:
        measured_temp = thermometer.temperature()
        print measured_temp
        pid_output = pid_controller.update(measured_temp, start_temp)
        heater.power(clamp(pid_output, 0.4))
        time.sleep(0.5)
        
    print "Finished preheating..."
    
    pid_controller.soft_reset()
        
    for target_temp in dec_range(start_temp, end_temp, temp_res):
        print "Adjusting temp to {t}".format(t=target_temp)
        pid_controller.time_reset()
        measured_temp = thermometer.temperature()
        while measured_temp < target_temp:
            measured_temp = thermometer.temperature()
            print measured_temp
            pid_output = pid_controller.update(measured_temp, target_temp)
            heater.power(clamp(pid_output,0.4))
            time.sleep(0.5)


        for i in range(60):
            measured_temp = thermometer.temperature()
            print measured_temp
            pid_output = pid_controller.update(measured_temp, target_temp)
            heater.power(clamp(pid_output,0.4))
            time.sleep(0.5)

        avg_iters = 40
        phold = 0
        for i in range(avg_iters):
            measured_temp = thermometer.temperature()
            print measured_temp
            pid_output = pid_controller.update(measured_temp, target_temp)
            heater.power(clamp(pid_output,0.4))
            phold += clamp(pid_output, 0.4)
            time.sleep(0.5)  
        phold = phold/avg_iters;
        print "Holding temperature for measurement."
        heater.power(phold)
        data.append(collectDataPoint())
        record_temp_file(inter_directory, index)
        print "Measurement taken."
        index += 1
    
    # record all of the data once finished
    file_path = os.path.join(base_directory, "FINALDATA")
    pickle.dump(data, open(file_path, 'wb+'))

    end_time = datetime.now()
    diff_time = end_time - start_time
    print "Experimental duration: " + str(diff_time)
    print data

    finishExperiment()

if __name__ == "__main__":
    arguments = sys.argv[1:]
    start_temp = float(arguments[0])
    end_temp = float(arguments[1])
    resolution = float(arguments[2])
    directory = os.path.join(os.getcwd(), arguments[3])

    runExperiment(start_temp, end_temp, resolution, directory)
    
