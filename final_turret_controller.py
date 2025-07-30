#!/usr/bin/env python3
"""
Final Water Turret Controller - MicroPython Approach
Works with modified CyberBrick Controller Core MicroPython code
Simple serial commands, no complex protocols needed
"""

import serial
import time
import logging
import threading
from raspberry_pi_receiver import ArduinoSensorReceiver, SensorReading

class CyberBrickMicroPythonInterface:
    """Simple serial interface for modified CyberBrick MicroPython code"""
    
    def __init__(self):
        self.serial_conn = None
        self.port = None
        self.is_connected = False
        self.auto_mode = False
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def connect(self, port: str = None) -> bool:
        """Connect to CyberBrick Controller Core"""
        test_ports = [port] if port else ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0", "/dev/ttyACM1"]
        
        for test_port in test_ports:
            try:
                ser = serial.Serial(test_port, 115200, timeout=2)
                time.sleep(1)
                
                # Test with status command
                ser.write(b"STATUS\n")
                response = ser.readline().decode().strip()
                
                if "STATUS:" in response:
                    self.serial_conn = ser
                    self.port = test_port
                    self.is_connected = True
                    self.logger.info(f"Connected to CyberBrick on {test_port}")
                    return True
                else:
                    ser.close()
                    
            except Exception as e:
                self.logger.debug(f"Port {test_port} failed: {e}")
                continue
                
        self.logger.error("Could not connect to CyberBrick Controller Core")
        return False
        
    def send_command(self, command: str) -> str:
        """Send command and get response"""
        if not self.is_connected:
            return ""
            
        try:
            self.serial_conn.write(f"{command}\n".encode())
            response = self.serial_conn.readline().decode().strip()
            self.logger.debug(f"Command: {command} → Response: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            return ""
            
    def enable_auto_mode(self) -> bool:
        """Switch to auto mode"""
        response = self.send_command("MODE:AUTO")
        if "AUTO_OK" in response:
            self.auto_mode = True
            self.logger.info("AUTO mode enabled")
            return True
        return False
        
    def enable_manual_mode(self) -> bool:
        """Switch to manual mode"""  
        response = self.send_command("MODE:MANUAL")
        if "MANUAL_OK" in response:
            self.auto_mode = False
            self.logger.info("MANUAL mode enabled")
            return True
        return False
        
    def move_turret(self, pwm1=None, pwm2=None, pwm3=None) -> bool:
        """Move turret using PWM values from Water+Turret.json"""
        if not self.auto_mode:
            return False
            
        # Build command with only specified values
        params = []
        if pwm1 is not None:
            params.append(f"PWM1={pwm1}")
        if pwm2 is not None:
            params.append(f"PWM2={pwm2}")
        if pwm3 is not None:
            params.append(f"PWM3={pwm3}")
            
        if params:
            command = f"MOVE:{','.join(params)}"
            response = self.send_command(command)
            return "OK" in response
            
        return False
        
    def fire_water(self, duration=0.5) -> bool:
        """Execute fire sequence using Water+Turret.json button mapping"""
        if not self.auto_mode:
            return False
            
        # Button down: PWM3=0 (fire)
        if self.move_turret(pwm3=0):
            time.sleep(duration)
            # Button up: PWM3=20 (stop, from your config)
            return self.move_turret(pwm3=20)
            
        return False
        
    def get_status(self) -> dict:
        """Get current Controller Core status"""
        response = self.send_command("STATUS")
        if response.startswith("STATUS:"):
            try:
                # Parse: STATUS:AUTO,90,90,90
                parts = response.split(":")[1].split(",")
                return {
                    "mode": parts[0],
                    "pwm1": int(parts[1]),
                    "pwm2": int(parts[2]), 
                    "pwm3": int(parts[3])
                }
            except:
                pass
        return {}
        
    def disconnect(self):
        """Disconnect and return to manual mode"""
        if self.is_connected:
            self.enable_manual_mode()
            time.sleep(0.1)
            self.serial_conn.close()
            
        self.is_connected = False

class FinalWaterTurretController:
    """Final simplified water turret controller"""
    
    def __init__(self):
        self.cyberbrick = CyberBrickMicroPythonInterface()
        self.sensor_receiver = None
        
        # Tracking state
        self.current_tilt = 90  # Center position
        self.target_detected = False
        self.last_fire_time = 0
        self.fire_cooldown = 2.0
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def connect_all_systems(self) -> bool:
        """Connect to CyberBrick and Arduino sensors"""
        # Connect to CyberBrick
        if not self.cyberbrick.connect():
            return False
            
        # Connect to Arduino sensors (different port than CyberBrick)
        sensor_ports = ['/dev/ttyACM0', '/dev/ttyUSB0', '/dev/ttyACM1', '/dev/ttyUSB1']
        for port in sensor_ports:
            if port == self.cyberbrick.port:
                continue
                
            self.sensor_receiver = ArduinoSensorReceiver(port=port)
            if self.sensor_receiver.connect():
                break
        else:
            self.logger.error("Could not connect to Arduino sensors")
            return False
            
        return True
        
    def auto_track_and_fire(self, reading: SensorReading):
        """Auto tracking with simplified logic"""
        if not self.cyberbrick.auto_mode:
            return
            
        # Target detection
        if reading.distance > 0 and reading.distance < 100:
            self.target_detected = True
            
            # Calculate tilt angle based on distance
            if reading.distance < 20:
                target_tilt = 80    # Close targets - aim down
            elif reading.distance < 50:
                target_tilt = 90    # Medium distance - level
            else:
                target_tilt = 100   # Far targets - aim up
                
            # Smooth movement
            if abs(self.current_tilt - target_tilt) > 3:
                step = 3 if target_tilt > self.current_tilt else -3
                self.current_tilt += step
                self.current_tilt = max(70, min(110, self.current_tilt))
                
                # Move turret
                self.cyberbrick.move_turret(pwm2=self.current_tilt)
                
            # Fire if conditions met
            if reading.sound_detected and reading.proximity_alert:
                current_time = time.time()
                if current_time - self.last_fire_time > self.fire_cooldown:
                    self.logger.info("🎯 Target acquired - FIRING! 💦")
                    self.cyberbrick.fire_water(0.5)
                    self.last_fire_time = current_time
                    
        else:
            # No target - return to center
            self.target_detected = False
            if self.current_tilt != 90:
                self.current_tilt = 90
                self.cyberbrick.move_turret(pwm2=90)
                
    def toggle_mode(self):
        """Toggle between manual and auto modes"""
        if self.cyberbrick.auto_mode:
            self.cyberbrick.enable_manual_mode()
        else:
            self.cyberbrick.enable_auto_mode()
            
    def run(self):
        """Main control loop"""
        if not self.connect_all_systems():
            self.logger.error("Failed to connect to systems")
            return
            
        self.logger.info("🚀 Final Water Turret Controller Started")
        self.logger.info("📡 Using official CyberBrick MicroPython interface")
        self.logger.info("🎮 Press Enter to toggle Manual/Auto mode")
        self.logger.info("🛑 Press Ctrl+C to exit")
        
        # Start in manual mode
        self.cyberbrick.enable_manual_mode()
        
        # Start input handler thread
        input_thread = threading.Thread(target=self.handle_input, daemon=True)
        input_thread.start()
        
        try:
            while True:
                # Process sensor data
                if self.sensor_receiver.serial_conn.in_waiting > 0:
                    line = self.sensor_receiver.serial_conn.readline().decode('utf-8').strip()
                    
                    if line.startswith("DATA:"):
                        reading = self.sensor_receiver.parse_data_line(line)
                        if reading:
                            self.auto_track_and_fire(reading)
                            
                            # Status logging every 5 seconds
                            if int(time.time()) % 5 == 0:
                                mode = "🤖 AUTO" if self.cyberbrick.auto_mode else "🎮 MANUAL"
                                target = "🎯 YES" if self.target_detected else "❌ NO"
                                self.logger.info(f"[{mode}] Distance: {reading.distance:.1f}cm, "
                                               f"Sound: {reading.sound_level}%, Target: {target}")
                
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Shutting down...")
        finally:
            self.cleanup()
            
    def handle_input(self):
        """Handle Enter key for mode switching"""
        while True:
            try:
                input()  # Wait for Enter
                self.toggle_mode()
                mode = "🤖 AUTO" if self.cyberbrick.auto_mode else "🎮 MANUAL"
                print(f"Switched to {mode} mode")
            except EOFError:
                break
                
    def cleanup(self):
        """Clean shutdown"""
        if self.cyberbrick:
            self.cyberbrick.disconnect()
        if self.sensor_receiver:
            self.sensor_receiver.disconnect()
        self.logger.info("✅ Cleanup complete")

def main():
    print("🏗️  Final Water Turret Controller")
    print("📋 Make sure you've modified the CyberBrick Controller Core with Pi interface!")
    print("🔗 See: https://github.com/CyberBrick-Official/CyberBrick_Controller_Core")
    print()
    
    controller = FinalWaterTurretController()
    controller.run()

if __name__ == "__main__":
    main() 