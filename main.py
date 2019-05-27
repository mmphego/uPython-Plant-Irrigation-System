from utils import read_config
from soil_moisture import MoistureSensor

if __name__ == "__main__":
    hour = 3600
    config = read_config("config.json")
    moisture_Sensor = MoistureSensor(0, config)
    try:
        moisture_Sensor.run_timer(secs=hour)
    except Exception:
        moisture_Sensor.stop_timer()
