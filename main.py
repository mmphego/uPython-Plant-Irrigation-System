from soil_moisture import MoistureSensor
from utils import read_config

if __name__ == "__main__":
    filename = "config.json"
    config = read_config(filename)
    moisture_Sensor = MoistureSensor(config)
    moisture_Sensor.run_timer(900)
