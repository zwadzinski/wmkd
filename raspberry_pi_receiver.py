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
from typing import Optional

from sensor_data_processor import SensorDataProcessor, SensorReading
from distance_sensor_receiver import DistanceSensorReceiver
from sound_sensor_receiver import SoundSensorReceiver

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
        
        # Initialize data processor and individual receivers
        self.data_processor = SensorDataProcessor()
        self.distance_receiver = DistanceSensorReceiver()
        self.sound_receiver = SoundSensorReceiver()
        
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
                
                # Parse individual sensor data using their receivers
                distance_reading = self.distance_receiver.parse_distance_data(data)
                sound_reading = self.sound_receiver.parse_sound_data(data)
                
                # Combine into complete sensor reading if both are valid
                if distance_reading and sound_reading:
                    return SensorReading(
                        timestamp=distance_reading.timestamp,
                        distance=distance_reading.distance,
                        sound_level=sound_reading.sound_level,
                        sound_raw=sound_reading.sound_raw,
                        sound_detected=sound_reading.sound_detected,
                        proximity_alert=distance_reading.proximity_alert,
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
            # Clear any initial garbage data
            time.sleep(0.5)  # Give Arduino time to start up
            self.serial_conn.reset_input_buffer()
            
            while True:
                if self.serial_conn.in_waiting > 0:
                    try:
                        # Read line with error handling for corrupted bytes
                        line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                    except UnicodeDecodeError:
                        # Skip corrupted data and continue
                        continue
                    
                    if not line:
                        continue
                    
                    # Handle different message types
                    if line.startswith("STATUS:"):
                        self.handle_status_message(line)
                    elif line.startswith("DATA:"):
                        reading = self.parse_data_line(line)
                        if reading:
                            self.data_processor.process_sensor_reading(reading)
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
            self.data_processor.handle_proximity_and_sound_alert()
        elif alert_type == "PROXIMITY_ONLY":
            self.data_processor.handle_proximity_alert()
        elif alert_type == "SOUND_ONLY":
            self.data_processor.sound_processor.handle_sound_alert()
    
    def set_proximity_callback(self, callback):
        """Set callback function for proximity alerts"""
        self.data_processor.set_proximity_callback(callback)
        self.data_processor.distance_processor.set_proximity_callback(callback)
    
    def set_sound_callback(self, callback):
        """Set callback function for sound alerts"""
        self.data_processor.sound_processor.set_sound_callback(callback)
    
    def set_proximity_and_sound_callback(self, callback):
        """Set callback function for proximity and sound alerts"""
        self.data_processor.set_proximity_and_sound_callback(callback)

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