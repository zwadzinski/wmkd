#!/usr/bin/env python3
"""
Pi Turret Controller for Modified CyberBrick Firmware
Provides manual/auto mode switching and intelligent turret control
"""

import serial
import time
import logging
import threading
from raspberry_pi_receiver import ArduinoSensorReceiver
from sensor_data_processor import SensorDataProcessor

class PiTurretController:
    def __init__(self, cyberbrick_port='/dev/ttyACM0', arduino_port='/dev/ttyACM1', baudrate=9600):
        """Initialize the Pi turret controller"""
        self.cyberbrick_port = cyberbrick_port
        self.arduino_port = arduino_port
        self.baudrate = baudrate
        self.cyberbrick_conn = None
        self.auto_mode = False
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize sensor system
        self.sensor_receiver = ArduinoSensorReceiver(port=arduino_port)
        self.sensor_processor = SensorDataProcessor()
        
        # Sensor data storage
        self.last_sensor_data = None
        self.sensor_thread = None
        self.running = False
        
    def connect_cyberbrick(self):
        """Connect to the modified CyberBrick firmware"""
        try:
            self.cyberbrick_conn = serial.Serial(
                port=self.cyberbrick_port,
                baudrate=self.baudrate,
                timeout=1
            )
            self.logger.info(f"Connected to CyberBrick on {self.cyberbrick_port}")
            time.sleep(1)  # Give device time to initialize
            return True
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect to CyberBrick: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from CyberBrick"""
        if self.cyberbrick_conn and self.cyberbrick_conn.is_open:
            # Switch back to manual mode before disconnecting
            self.set_manual_mode()
            self.cyberbrick_conn.close()
            self.logger.info("Disconnected from CyberBrick")
    
    def send_command(self, command):
        """Send a command to CyberBrick"""
        if not self.cyberbrick_conn or not self.cyberbrick_conn.is_open:
            self.logger.error("No CyberBrick connection")
            return False
            
        try:
            self.cyberbrick_conn.write(f"{command}\n".encode('utf-8'))
            self.logger.debug(f"Sent: {command}")
            
            # Wait for response
            time.sleep(0.1)
            if self.cyberbrick_conn.in_waiting > 0:
                response = self.cyberbrick_conn.readline().decode('utf-8', errors='ignore').strip()
                self.logger.debug(f"Response: {response}")
                return response
            return True
        except Exception as e:
            self.logger.error(f"Command failed '{command}': {e}")
            return False
    
    def set_auto_mode(self):
        """Switch CyberBrick to auto mode (Pi control)"""
        response = self.send_command("MODE:AUTO")
        if "AUTO_OK" in str(response):
            self.auto_mode = True
            self.logger.info("🤖 AUTO MODE - Pi controls turret")
            return True
        else:
            self.logger.error("Failed to enable auto mode")
            return False
    
    def set_manual_mode(self):
        """Switch CyberBrick to manual mode (RF control)"""
        response = self.send_command("MODE:MANUAL")
        if "MANUAL_OK" in str(response):
            self.auto_mode = False
            self.logger.info("🎮 MANUAL MODE - RF controller active")
            return True
        else:
            self.logger.error("Failed to enable manual mode")
            return False
    
    def fire_turret(self):
        """Fire the water turret"""
        if not self.auto_mode:
            self.logger.warning("Cannot fire - not in auto mode")
            return False
            
        # Fire sequence based on Water+Turret.json
        self.send_command("MOVE:PWM3=0")   # Fire
        time.sleep(0.5)                    # Brief fire duration
        self.send_command("MOVE:PWM3=20")  # Stop
        self.logger.info("💦 FIRED!")
        return True
    
    def aim_turret(self, rotation=90, tilt=90):
        """Aim the turret to specific angles"""
        if not self.auto_mode:
            self.logger.warning("Cannot aim - not in auto mode")
            return False
            
        # Clamp values to valid ranges (from Water+Turret.json)
        rotation = max(0, min(180, rotation))
        tilt = max(0, min(180, tilt))
        
        command = f"MOVE:PWM1={rotation},PWM2={tilt}"
        self.send_command(command)
        self.logger.info(f"🎯 Aimed: Rotation={rotation}°, Tilt={tilt}°")
        return True
    
    def start_sensor_monitoring(self):
        """Start monitoring sensor data in background thread"""
        if self.sensor_receiver.connect():
            self.running = True
            self.sensor_thread = threading.Thread(target=self._sensor_monitor_loop)
            self.sensor_thread.daemon = True
            self.sensor_thread.start()
            self.logger.info("📡 Sensor monitoring started")
        else:
            self.logger.error("Failed to connect to sensors")
    
    def _sensor_monitor_loop(self):
        """Background thread for sensor monitoring"""
        try:
            while self.running:
                # This would need to be adapted to work with the existing receiver
                # For now, just simulate sensor data
                time.sleep(0.1)
        except Exception as e:
            self.logger.error(f"Sensor monitoring error: {e}")
    
    def intelligent_tracking(self):
        """Auto-tracking mode based on sensor data"""
        self.logger.info("🎯 Starting intelligent tracking mode")
        
        while self.auto_mode and self.running:
            try:
                # Get latest sensor data (placeholder - would integrate with sensor receiver)
                # distance = self.last_sensor_data.distance if self.last_sensor_data else 100
                # sound_detected = self.last_sensor_data.sound_detected if self.last_sensor_data else False
                
                # Placeholder intelligent tracking logic
                # if distance < 50 and sound_detected:
                #     self.logger.info("🎯 Target detected - aiming and firing!")
                #     self.aim_turret(90, 85)  # Aim slightly down
                #     time.sleep(1)
                #     self.fire_turret()
                #     time.sleep(2)  # Cooldown
                
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Tracking error: {e}")
                break
    
    def interactive_mode(self):
        """Interactive mode for testing and manual control"""
        self.logger.info("🎮 Interactive mode - Press Enter to toggle Manual/Auto")
        
        try:
            while True:
                input("Press Enter to toggle mode (Ctrl+C to exit)...")
                
                if self.auto_mode:
                    self.set_manual_mode()
                else:
                    if self.set_auto_mode():
                        # Test fire when switching to auto
                        self.logger.info("Testing fire sequence...")
                        time.sleep(1)
                        self.fire_turret()
                        
        except KeyboardInterrupt:
            self.logger.info("Exiting interactive mode...")

def main():
    """Main function"""
    controller = PiTurretController()
    
    if not controller.connect_cyberbrick():
        return
    
    try:
        # Start sensor monitoring
        controller.start_sensor_monitoring()
        
        # Run interactive mode
        controller.interactive_mode()
        
    finally:
        controller.running = False
        controller.disconnect()

if __name__ == "__main__":
    main()