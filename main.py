from utils import read_config
from soil_moisture import MoistureSensor

if __name__ == "__main__":

    config = read_config("config.json")
    moisture_Sensor = MoistureSensor(0, config)
    moisture_Sensor.run()
