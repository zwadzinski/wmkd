#!/usr/bin/env python3
"""
Sound Sensor Processor
Handles all logic for processing and responding to sound sensor data
"""

import logging
from typing import Optional, Callable
from sound_sensor_receiver import SoundReading


class SoundSensorProcessor:
    def __init__(self):
        """Initialize the sound sensor processor"""
        self.logger = logging.getLogger(__name__)
        
        # Callback function for custom actions
        self.on_sound_callback: Optional[Callable] = None
        
    def set_sound_callback(self, callback: Callable):
        """Set callback function for sound alerts"""
        self.on_sound_callback = callback
    
    def process_sound_reading(self, reading: SoundReading):
        """Process a sound sensor reading"""
        # Log the reading
        self.logger.info(
            f"Sound: {reading.sound_level:3d}% | "
            f"Raw: {reading.sound_raw:4d} | "
            f"Detected: {'Yes' if reading.sound_detected else 'No'}"
        )
        
        # Make sound-based decisions
        self.make_sound_decisions(reading)
        
        # Check sound conditions
        self.check_sound_conditions(reading)
    
    def make_sound_decisions(self, reading: SoundReading):
        """Make real-time decisions based on sound data"""
        if reading.sound_detected:
            if reading.sound_level > 80:
                self.logger.warning("LOUD sound detected - possible alert condition")
                # Your action: Investigate, record event, etc.
            elif reading.sound_level > 50:
                self.logger.info("Moderate sound detected")
                # Your action: Increase monitoring sensitivity, etc.
            else:
                self.logger.debug("Low level sound detected")
                # Your action: Normal monitoring, etc.
    
    def check_sound_conditions(self, reading: SoundReading):
        """Check for custom sound conditions and trigger actions"""
        # Example: Alert if very loud sound (> 80%)
        if reading.sound_level > 80:
            self.logger.warning(f"Very loud sound detected: {reading.sound_level}%")
    
    def handle_sound_alert(self):
        """Handle sound alert"""
        self.logger.info("ALERT: Sound detected")
        if self.on_sound_callback:
            self.on_sound_callback()