#!/usr/bin/env python3
"""
Sensor Data Processor
Coordinates processing of data from multiple sensors
"""

import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Callable

from distance_sensor_processor import DistanceSensorProcessor
from sound_sensor_processor import SoundSensorProcessor
from distance_sensor_receiver import DistanceReading
from sound_sensor_receiver import SoundReading


@dataclass
class SensorReading:
    timestamp: int
    distance: float
    sound_level: int
    sound_raw: int
    sound_detected: bool
    proximity_alert: bool
    received_at: datetime


class SensorDataProcessor:
    def __init__(self):
        """Initialize the sensor data processor"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize individual sensor processors
        self.distance_processor = DistanceSensorProcessor()
        self.sound_processor = SoundSensorProcessor()
        
        # Callback functions for custom actions
        self.on_proximity_callback: Optional[Callable] = None
        self.on_proximity_and_sound_callback: Optional[Callable] = None
        
    def set_proximity_callback(self, callback: Callable):
        """Set callback function for proximity alerts"""
        self.on_proximity_callback = callback
    
    def set_proximity_and_sound_callback(self, callback: Callable):
        """Set callback function for proximity and sound alerts"""
        self.on_proximity_and_sound_callback = callback
    
    def process_sensor_reading(self, reading: SensorReading):
        """Process a complete sensor reading by delegating to individual processors"""
        # Create individual sensor readings
        distance_reading = DistanceReading(
            timestamp=reading.timestamp,
            distance=reading.distance,
            proximity_alert=reading.proximity_alert,
            received_at=reading.received_at
        )
        
        sound_reading = SoundReading(
            timestamp=reading.timestamp,
            sound_level=reading.sound_level,
            sound_raw=reading.sound_raw,
            sound_detected=reading.sound_detected,
            received_at=reading.received_at
        )
        
        # Process with individual processors
        self.distance_processor.process_distance_reading(distance_reading)
        self.sound_processor.process_sound_reading(sound_reading)
        
        # Check for combined conditions
        self.check_combined_conditions(reading)
    
    def check_combined_conditions(self, reading: SensorReading):
        """Check for conditions that require multiple sensors"""
        # Combined conditions for complex decisions
        if reading.proximity_alert and reading.sound_detected:
            self.logger.critical("DUAL ALERT: Close object AND sound!")
            # Your action: High priority response, emergency protocols, etc.
            if self.on_proximity_and_sound_callback:
                self.on_proximity_and_sound_callback()
        
        # Add more combined sensor logic here
        # Examples:
        # - If object is close but no sound, might be a quiet approach
        # - If sound but no object, might be distant noise
        # - Patterns over time combining both sensors
    
    def handle_proximity_alert(self):
        """Handle proximity-only alert by delegating to distance processor"""
        self.distance_processor.handle_proximity_alert()
        if self.on_proximity_callback:
            self.on_proximity_callback()
    
    def handle_proximity_and_sound_alert(self):
        """Handle combined proximity and sound alert"""
        self.logger.warning("ALERT: Object close AND sound detected!")
        # Delegate to individual processors
        self.distance_processor.handle_proximity_alert()
        self.sound_processor.handle_sound_alert()
        
        if self.on_proximity_and_sound_callback:
            self.on_proximity_and_sound_callback()
        # Add your custom logic here
        # Example: Send notification, trigger camera, etc.