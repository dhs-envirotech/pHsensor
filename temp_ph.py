import spidev
import time
from collections import deque

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, CE0
spi.max_speed_hz = 1350000

# Function to read SPI data from MCP3008 channel (0-7)
def read_channel(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# Function to convert ADC data to voltage
def convert_volts(data, vref=3.3):
    volts = (data * vref) / float(1023)
    return volts

# Function to convert voltage to pH (calibration required)
def convert_ph(voltage):
    # Calibration values; adjust these based on your pH calibration (known values for pH 4, 7, and 10)
    neutral_voltage = 2.5  # Replace this with the actual voltage at pH 7 from calibration
    slope = -3.0           # Adjust based on calibration with known buffer solutions
    pH = 7 + (voltage - neutral_voltage) * slope
    return pH

# Moving average filter to smooth out readings
def moving_average(data_points, new_data, window_size=5):
    data_points.append(new_data)
    if len(data_points) > window_size:
        data_points.popleft()
    return sum(data_points) / len(data_points)

# Function to convert voltage to temperature (example conversion, adjust as needed)
def convert_to_temperature(voltage):
    # Example logic for temperature conversion
    # Assuming a linear sensor output: 0.5V at 0°C and 10mV/°C sensitivity
    temperature = (voltage - 0.5) * 100  # Adjust based on your specific sensor
    return temperature

try:
    # Initialize deques for smoothing pH and temperature readings
    ph_data_points = deque()
    temp_data_points = deque()
    
    while True:
        # Read from channel 0 (pH sensor)
        ph_adc_value = read_channel(0)
        ph_voltage = convert_volts(ph_adc_value)
        smoothed_ph_voltage = moving_average(ph_data_points, ph_voltage)
        pH_value = convert_ph(smoothed_ph_voltage)
        
        # Read from channel 1 (Temperature sensor)
        temp_adc_value = read_channel(1)
        temp_voltage = convert_volts(temp_adc_value)
        smoothed_temp_voltage = moving_average(temp_data_points, temp_voltage)
        temperature = convert_to_temperature(smoothed_temp_voltage)
        
        # Print the results
        print(f"pH Sensor - ADC: {ph_adc_value}, Voltage: {ph_voltage:.3f} V, Smoothed Voltage: {smoothed_ph_voltage:.3f} V, pH: {pH_value:.2f}")
        print(f"Temp Sensor - ADC: {temp_adc_value}, Voltage: {temp_voltage:.3f} V, Smoothed Voltage: {smoothed_temp_voltage:.3f} V, Temperature: {temperature:.2f} °C")
        
        # Wait for a second before the next reading
        time.sleep(1)

except KeyboardInterrupt:
    pass

finally:
    spi.close()
