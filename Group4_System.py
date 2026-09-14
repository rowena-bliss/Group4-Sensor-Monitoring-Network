"""
CSC2105: Object-Oriented Programming Using Python
Group Project - Topic 5: Scalable OOP System
Group 4 - Sensor Monitoring Network

Group members:
- [Full Name 1]
- [Full Name 2]
- [Full Name 3]
- [Full Name 4]
(Replace the placeholders above with your actual group member names.)

Scenario:
An engineering laboratory monitors equipment using digital sensors.
Each sensor has an identity, a location, a unit of measurement, a
current reading, and lower/upper limits that define its acceptable
range. Technicians update a sensor with new readings, and the system
reports whether the reading is normal, too low, or too high, and
whether that situation counts as an alarm.
"""


class Sensor:
    """Represents a single digital sensor in the lab."""

    def __init__(self, sensor_id, location, unit, lower_limit, upper_limit):
        # Basic validation on construction: the limits themselves must make sense.
        if lower_limit >= upper_limit:
            raise ValueError(
                f"Invalid limits for sensor {sensor_id}: "
                f"lower_limit ({lower_limit}) must be less than upper_limit ({upper_limit})."
            )

        self.sensor_id = sensor_id
        self.location = location
        self.unit = unit
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.reading = None  # No reading has been taken yet.

    def update_reading(self, new_reading):
        """
        Update the sensor with a new reading.

        Returns True if the reading was accepted, False if it was refused.
        An invalid reading (not a number) is refused rather than silently
        ignored or allowed to corrupt the sensor's state.
        """
        if not isinstance(new_reading, (int, float)) or isinstance(new_reading, bool):
            print(
                f"[REFUSED] Sensor {self.sensor_id}: reading must be a number, "
                f"got {new_reading!r}."
            )
            return False

        self.reading = new_reading
        return True

    def get_status(self):
        """Return 'no reading', 'too low', 'too high', or 'normal'."""
        if self.reading is None:
            return "no reading"
        if self.reading < self.lower_limit:
            return "too low"
        if self.reading > self.upper_limit:
            return "too high"
        return "normal"

    def is_alarm(self):
        """A sensor is in an alarm state if its reading is out of range."""
        return self.get_status() in ("too low", "too high")

    def display(self):
        """Print a clear summary of the sensor's current state."""
        status = self.get_status()
        alarm_flag = " *** ALARM ***" if self.is_alarm() else ""
        reading_text = (
            f"{self.reading} {self.unit}" if self.reading is not None else "N/A"
        )
        print(
            f"Sensor {self.sensor_id} | Location: {self.location} | "
            f"Reading: {reading_text} | Status: {status}{alarm_flag}"
        )

    def __str__(self):
        status = self.get_status()
        reading_text = (
            f"{self.reading} {self.unit}" if self.reading is not None else "N/A"
        )
        return (
            f"Sensor({self.sensor_id}, {self.location}, "
            f"reading={reading_text}, status={status})"
        )


def run_demo():
    print("=== Sensor Monitoring Network Demo ===\n")

    # Step 1: Create two sensors — a temperature sensor and a voltage sensor.
    temp_sensor = Sensor("TEMP-01", "Server Room A", "°C", lower_limit=18, upper_limit=27)
    volt_sensor = Sensor("VOLT-01", "Panel B", "V", lower_limit=210, upper_limit=240)

    # Step 2: Give each sensor a normal reading (inside its acceptable range).
    print("Step 2: Normal readings")
    temp_sensor.update_reading(22.5)
    volt_sensor.update_reading(225)
    temp_sensor.display()
    volt_sensor.display()

    # Step 3: Give each sensor a reading outside its range -> alarm.
    print("\nStep 3: Out-of-range readings")
    temp_sensor.update_reading(31.0)   # above 27 -> too high
    volt_sensor.update_reading(195)    # below 210 -> too low
    temp_sensor.display()
    volt_sensor.display()

    # Step 4: Try an invalid update (text instead of a number) -> refused.
    print("\nStep 4: Invalid update is refused")
    temp_sensor.update_reading("hot")
    temp_sensor.display()  # reading stays at 31.0, unchanged


if __name__ == "__main__":
    run_demo()
