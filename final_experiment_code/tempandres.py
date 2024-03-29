# TEMPANDRES.py
# Defines auxilliary functions to handle resistivity calculations at various temperatures
from numpy import interp

therm_voltages = [1.644290, 1.642990, 1.641570, 1.640030, 1.638370, 1.636600, 1.634720, 1.632740, 1.630670, 1.628520, 1.626290, 1.624000, 1.621660, 1.619280, 1.616870, 1.614450, 1.612000, 1.609510, 1.606970, 1.604380, 1.601730, 1.599020, 1.596260, 1.59344, 1.59057, 1.58764, 1.58465, 1.57848, 1.57202, 1.56533, 1.55845, 1.55145, 1.54436, 1.53721, 1.53000, 1.52273, 1.51541, 1.49698, 1.47868, 1.46086, 1.44374, 1.42747, 1.41207, 1.39751, 1.38373, 1.37065, 1.35820, 1.34632, 1.33499, 1.32416, 1.31381, 1.30390, 1.29439, 1.28526, 1.27645, 1.26794, 1.25967, 1.25161, 1.24372, 1.23596, 1.22830, 1.22070, 1.21311, 1.20548, 1.197748, 1.181548, 1.162797, 1.140817, 1.125923, 1.119448, 1.115658, 1.112810, 1.110421, 1.108261, 1.106244, 1.104324, 1.102476, 1.100681, 1.098930, 1.097216, 1.095534, 1.093878, 1.092244, 1.090627, 1.089024, 1.085842, 1.082669, 1.079492, 1.076303, 1.073099, 1.069881, 1.066650, 1.063403, 1.060141, 1.056862, 1.048584, 1.040183, 1.031651, 1.027594, 1.022984, 1.014181, 1.005244, 0.986974, 0.968209, 0.949000, 0.929390, 0.909416, 0.889114, 0.868518, 0.847659, 0.826560, 0.805242, 0.783720, 0.762007, 0.740115, 0.718054, 0.695834, 0.673462, 0.650949, 0.628302, 0.621141, 0.605528, 0.582637, 0.559639, 0.536542, 0.513361, 0.490106, 0.466760, 0.443371, 0.419960, 0.396503, 0.373002, 0.349453, 0.325839, 0.302161, 0.278416, 0.254592, 0.230697, 0.206758, 0.182832, 0.159010, 0.135480, 0.112553, 0.090681]
therm_temps = [1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.2, 4.4, 4.6, 4.8, 5.0, 5.2, 5.4, 5.6, 5.8, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0, 37.0, 38.0, 39.0, 40.0, 42.0, 44.0, 46.0, 48.0, 50.0, 52.0, 54.0, 56.0, 58.0, 60.0, 65.0, 70.0, 75.0, 77.35, 80.0, 85.0, 90.0, 100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0, 180.0, 190.0, 200.0, 210.0, 220.0, 230.0, 240.0, 250.0, 260.0, 270.0, 273.0, 280.0, 290.0, 300.0, 310.0, 320.0, 330.0, 340.0, 350.0, 360.0, 370.0, 380.0, 390.0, 400.0, 410.0, 420.0, 430.0, 440.0, 450.0, 460.0, 470.0, 480.0, 490.0, 500.0]
therm_voltages_r = therm_voltages[::-1]
therm_temps_r = therm_temps[::-1]

plat_cal_celsius = [-200, -195, -190, -185, -180, -175, -170, -165, -160, -155, -150, -145, -140, -135, -130, -125, -120, -115, -110, -105, -100, -95, -90, -85, -80, -75, -70, -65, -60, -55, -50, -45, -40, -35, -30, -25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175, 180, 185, 190, 195, 200, 205, 210, 215, 220, 225, 230, 235]
plat_cal_ohms = [18.52, 20.68, 22.83, 24.97, 27.10, 29.22, 31.33, 33.44, 35.54, 37.64, 39.72, 41.80, 43.88, 45.94, 48.00, 50.06, 52.11, 54.15, 56.19, 58.23, 60.26, 62.28, 64.30, 66.31, 68.33, 70.33, 72.33, 74.33, 76.33, 78.32, 80.31, 82.29, 84.27, 86.25, 88.22, 90.19, 92.16, 94.12, 96.09, 98.04, 100.00, 101.95, 103.90, 105.85, 107.79, 109.73, 111.67, 113.61, 115.54, 117.47, 119.40, 121.32, 123.24, 125.16, 127.08, 128.99, 130.90, 132.80, 134.71, 136.61, 138.51, 140.40, 142.29, 144.18, 146.07, 147.95, 149.83, 151.71, 153.58, 155.46, 157.33, 159.19, 161.05, 162.91, 164.77, 166.63, 168.48, 170.33, 172.17, 174.02, 175.86, 177.69, 179.53, 181.36, 183.19, 185.01, 186.84, 188.66]

plat_cal_kelvin = [(t + 273.15) for t in plat_cal_celsius]
plat_cal_kelvin_r = plat_cal_kelvin[::-1]
plat_cal_ohms_r = plat_cal_ohms[::-1]

# resistivity units ohm meters * 10^-8
copper_resistivity_t   = [4, 10, 20, 50, 77, 100, 150, 200, 250, 295, 400]
copper_resistivity_rho = [0.015, 0.015, 0.017, 0.084, 0.21, 0.34, 0.70, 1.07, 1.41, 1.70, 2.38]
nichrome_resistivity_t = [4, 298]
nichrome_resistivity_rho = [105, 110]

# natural units
copper_resistivity_rho = [10**(-8) * rho for rho in copper_resistivity_rho]
nichrome_resistivity_rho = [10**(-8) * rho for rho in nichrome_resistivity_rho]

copper_resistivity = zip(copper_resistivity_t, copper_resistivity_rho)
nichrome_resistivity = zip(nichrome_resistivity_t, nichrome_resistivity_rho)

resistivity_tables = {"Copper": copper_resistivity, "Nichrome": nichrome_resistivity}

def resistivity(type, T):
        return 0

def temperature_from_voltage(V):
        return interp(V, therm_voltages_r, therm_temps_r)

def voltage_from_temperature(T):
        return interp(T, therm_temps, therm_voltages)

def temperature_from_resistance(R):
        return interp(R, plat_cal_ohms, plat_cal_kelvin)

def resistance_from_temperature(T):
        return interp(T, plat_cal_kelvin, plat_cal_ohms)
