#!/usr/bin/env python3
"""
Raspberry Pi Serial Receiver for Arduino Sensor Data
Receives data from Arduino running the combined sensor program
"""

import serial
import json
import time
import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class SensorReading:
    timestamp: int
    distance: float
    sound_level: int
    sound_raw: int
    sound_detected: bool
    proximity_alert: bool
    received_at: datetime

class ArduinoSensorReceiver:
    def __init__(self, port='/dev/ttyACM0', baudrate=9600, timeout=1):
        """
        Initialize the Arduino sensor receiver
        
        Args:
            port: Serial port (usually /dev/ttyACM0 or /dev/ttyUSB0)
            baudrate: Serial communication speed (must match Arduino)
            timeout: Serial read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        self.is_calibrating = True
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def connect(self):
        """Establish serial connection to Arduino"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.logger.info(f"Connected to Arduino on {self.port}")
            time.sleep(2)  # Give Arduino time to reset
            return True
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect to {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.logger.info("Disconnected from Arduino")
    
    def parse_data_line(self, line: str) -> Optional[SensorReading]:
        """Parse a DATA line from Arduino into SensorReading object"""
        try:
            if line.startswith("DATA:"):
                # Extract JSON part
                json_str = line[5:]  # Remove "DATA:" prefix
                data = json.loads(json_str)
                
                return SensorReading(
                    timestamp=data['timestamp'],
                    distance=data['distance'],
                    sound_level=data['sound_level'],
                    sound_raw=data['sound_raw'],
                    sound_detected=data['sound_detected'],
                    proximity_alert=data['proximity_alert'],
                    received_at=datetime.now()
                )
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.warning(f"Failed to parse data line: {line.strip()} - {e}")
        
        return None
    
    def read_sensor_data(self):
        """Main loop to read and process sensor data"""
        if not self.serial_conn or not self.serial_conn.is_open:
            self.logger.error("No serial connection established")
            return
        
        self.logger.info("Starting sensor data collection...")
        
        try:
            while True:
                if self.serial_conn.in_waiting > 0:
                    line = self.serial_conn.readline().decode('utf-8').strip()
                    
                    if not line:
                        continue
                    
                    # Handle different message types
                    if line.startswith("STATUS:"):
                        self.handle_status_message(line)
                    elif line.startswith("DATA:"):
                        reading = self.parse_data_line(line)
                        if reading:
                            self.process_sensor_reading(reading)
                    elif line.startswith("ALERT:"):
                        self.handle_alert_message(line)
                    elif line.startswith("CALIBRATION:"):
                        self.handle_calibration_message(line)
                    else:
                        # Log any other messages for debugging
                        self.logger.debug(f"Arduino: {line}")
                
                time.sleep(0.01)  # Small delay to prevent CPU overload
                
        except KeyboardInterrupt:
            self.logger.info("Stopping sensor data collection...")
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
    
    def handle_status_message(self, line: str):
        """Handle status messages from Arduino"""
        status = line.split(":", 1)[1]
        if status == "CALIBRATING":
            self.is_calibrating = True
            self.logger.info("Arduino is calibrating microphone...")
        elif status == "READY":
            self.is_calibrating = False
            self.logger.info("Arduino calibration complete - ready for data")
    
    def handle_calibration_message(self, line: str):
        """Handle calibration progress messages"""
        try:
            values = line.split(":", 1)[1].split(",")
            min_val, max_val, current_val = map(int, values)
            self.logger.debug(f"Calibration: Min={min_val}, Max={max_val}, Current={current_val}")
        except ValueError:
            pass
    
    def handle_alert_message(self, line: str):
        """Handle alert messages from Arduino"""
        alert_type = line.split(":", 1)[1]
        if alert_type == "PROXIMITY_AND_SOUND":
            self.logger.warning("ALERT: Object close AND sound detected!")
            self.on_proximity_and_sound_alert()
        elif alert_type == "PROXIMITY_ONLY":
            self.logger.info("ALERT: Object proximity detected")
            self.on_proximity_alert()
    
    def process_sensor_reading(self, reading: SensorReading):
        """Process a complete sensor reading for real-time decision making"""
        # Log the reading
        self.logger.info(
            f"Distance: {reading.distance:6.1f}cm | "
            f"Sound: {reading.sound_level:3d}% | "
            f"Detected: {'Yes' if reading.sound_detected else 'No'} | "
            f"Proximity: {'Yes' if reading.proximity_alert else 'No'}"
        )
        
        # Real-time decision making based on sensor data
        self.make_realtime_decisions(reading)
        
        # Check for custom conditions
        self.check_custom_conditions(reading)
    
    def make_realtime_decisions(self, reading: SensorReading):
        """Make real-time decisions based on sensor data"""
        # This is where you'll implement your decision-making logic
        # Examples of what you might do:
        
        # Example 1: Different responses based on distance ranges
        if reading.distance > 0:  # Valid distance reading
            if reading.distance < 5:
                self.logger.warning("CRITICAL: Object very close!")
                # Your action: Emergency stop, activate LED, sound alarm, etc.
                
            elif reading.distance < 20:
                self.logger.info("CAUTION: Object nearby")
                # Your action: Slow down, prepare to stop, etc.
                
            elif reading.distance < 50:
                self.logger.debug("Object detected in range")
                # Your action: Monitor, adjust course, etc.
        
        # Example 2: Sound-based decisions
        if reading.sound_detected:
            if reading.sound_level > 80:
                self.logger.warning("LOUD sound detected - possible alert condition")
                # Your action: Investigate, record event, etc.
            elif reading.sound_level > 50:
                self.logger.info("Moderate sound detected")
                # Your action: Increase monitoring sensitivity, etc.
        
        # Example 3: Combined conditions for complex decisions
        if reading.proximity_alert and reading.sound_detected:
            self.logger.critical("DUAL ALERT: Close object AND sound!")
            # Your action: High priority response, emergency protocols, etc.
        
        # Add your custom decision logic here
        # You have access to:
        # - reading.distance (float, -1 if invalid)
        # - reading.sound_level (int, 0-100%)
        # - reading.sound_raw (int, raw analog value)
        # - reading.sound_detected (bool)
        # - reading.proximity_alert (bool)
        # - reading.timestamp (Arduino millis)
        # - reading.received_at (Python datetime)
    
    def check_custom_conditions(self, reading: SensorReading):
        """Check for custom conditions and trigger actions"""
        # Example: Alert if very close object (< 10cm)
        if reading.distance > 0 and reading.distance < 10:
            self.logger.warning(f"Very close object detected: {reading.distance:.1f}cm")
        
        # Example: Alert if very loud sound (> 80%)
        if reading.sound_level > 80:
            self.logger.warning(f"Very loud sound detected: {reading.sound_level}%")
    
    def on_proximity_alert(self):
        """Called when proximity-only alert is triggered"""
        # Add your custom logic here
        pass
    
    def on_proximity_and_sound_alert(self):
        """Called when both proximity and sound alert is triggered"""
        # Add your custom logic here
        # Example: Send notification, trigger camera, etc.
        pass

def main():
    """Main function"""
    # Try common Arduino ports
    ports = ['/dev/ttyACM0', '/dev/ttyUSB0', '/dev/ttyACM1', '/dev/ttyUSB1']
    
    receiver = None
    for port in ports:
        receiver = ArduinoSensorReceiver(port=port)
        if receiver.connect():
            break
    else:
        print("Could not connect to Arduino on any common port.")
        print("Available ports might be:")
        print("  /dev/ttyACM0 - Most common for Arduino Uno/Nano")
        print("  /dev/ttyUSB0 - Common for Arduino with USB-to-serial chip")
        print("Run 'ls /dev/tty*' to see available ports")
        return
    
    try:
        # Start reading data for real-time processing
        receiver.read_sensor_data()
        
    finally:
        receiver.disconnect()

if __name__ == "__main__":
    main() 