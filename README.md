# Group4-Sensor-Monitoring-Network
Group 4 project – Sensor Monitoring Network implemented using Python OOP.

class Sensor:
    def __init__(self, sensor_id, location, unit, lower_limit, upper_limit):
        self.sensor_id = sensor_id
        self.location = location
        self.unit = unit
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.current = None
