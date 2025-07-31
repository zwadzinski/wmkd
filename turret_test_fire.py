#!/usr/bin/env python3
"""
Simple Turret Fire Test Script
Fires the turret gun once every 5 seconds to test the control interface
"""

import serial
import time
import logging

class TurretFireTest:
    def __init__(self, port='/dev/ttyACM0', baudrate=9600, timeout=1):
        """Initialize turret fire test"""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def connect(self):
        """Establish serial connection to CyberBrick"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.logger.info(f"Connected to CyberBrick on {self.port}")
            time.sleep(1)  # Give device time to initialize
            return True
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect to {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Close serial connection"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.logger.info("Disconnected from CyberBrick")
    
    def send_command(self, command):
        """Send a command to the CyberBrick"""
        if not self.serial_conn or not self.serial_conn.is_open:
            self.logger.error("No serial connection established")
            return False
            
        try:
            # Send command
            self.serial_conn.write(f"{command}\n".encode('utf-8'))
            self.logger.info(f"Sent command: {command}")
            
            # Wait for response (optional)
            time.sleep(0.1)
            if self.serial_conn.in_waiting > 0:
                response = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                if response:
                    self.logger.info(f"Response: {response}")
                    
            return True
        except Exception as e:
            self.logger.error(f"Failed to send command '{command}': {e}")
            return False
    
    def fire_sequence(self):
        """Execute fire sequence - try different command formats"""
        commands_to_try = [
            "FIRE",                    # Simple fire command
            "MODE:FIRE",              # Mode-based command
            "MOVE:PWM3=0",            # Direct PWM control (fire)
            "ACTION:FIRE",            # Action-based command
            "TURRET:FIRE",            # Turret-specific command
        ]
        
        self.logger.info("🎯 Attempting to fire turret...")
        
        for command in commands_to_try:
            self.logger.info(f"Trying command: {command}")
            if self.send_command(command):
                time.sleep(0.5)  # Brief pause between commands
            else:
                break
                
        # Try to stop/reset after firing
        self.logger.info("Sending stop command...")
        self.send_command("STOP")
        self.send_command("MOVE:PWM3=20")  # Reset position (based on docs)
    
    def continuous_fire_test(self, interval=5):
        """Fire every X seconds continuously"""
        self.logger.info("🚀 Starting continuous fire test")
        self.logger.info(f"🎯 Will fire every {interval} seconds")
        self.logger.info("🛑 Press Ctrl+C to stop")
        
        fire_count = 1
        try:
            while True:
                self.logger.info(f"🔥 FIRE #{fire_count}")
                self.fire_sequence()
                
                self.logger.info(f"⏱️  Waiting {interval} seconds until next fire...")
                time.sleep(interval)
                fire_count += 1
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Fire test stopped by user")
        except Exception as e:
            self.logger.error(f"🚨 Error during fire test: {e}")

def main():
    """Main function"""
    # Hardcoded port based on device identification:
    # /dev/ttyACM0 = CyberBrick Core A11 (Espressif) - TURRET CONTROL
    # /dev/ttyACM1 = Arduino Mega 2560 R3 - ARDUINO SENSORS
    cyberbrick_port = '/dev/ttyACM0'  # CyberBrick for turret control
    
    turret = TurretFireTest(port=cyberbrick_port)
    if not turret.connect():
        print(f"Could not connect to CyberBrick on {cyberbrick_port}")
        print("Device mapping:")
        print("  /dev/ttyACM0 - CyberBrick Core A11 (Espressif)")
        print("  /dev/ttyACM1 - Arduino Mega 2560 R3")
        print("Run 'lsusb' to verify devices are connected")
        return
    
    try:
        # Start continuous fire test (every 5 seconds)
        turret.continuous_fire_test(interval=5)
        
    finally:
        turret.disconnect()

if __name__ == "__main__":
    main()