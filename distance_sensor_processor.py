#!/usr/bin/env python3
"""
Distance Sensor Processor
Handles all logic for processing and responding to distance sensor data
"""

import logging
from typing import Optional, Callable
from distance_sensor_receiver import DistanceReading


class DistanceSensorProcessor:
    def __init__(self):
        """Initialize the distance sensor processor"""
        self.logger = logging.getLogger(__name__)
        
        # Callback function for custom actions
        self.on_proximity_callback: Optional[Callable] = None
        
    def set_proximity_callback(self, callback: Callable):
        """Set callback function for proximity alerts"""
        self.on_proximity_callback = callback
    
    def process_distance_reading(self, reading: DistanceReading):
        """Process a distance sensor reading"""
        # Log the reading
        self.logger.info(
            f"Distance: {reading.distance:6.1f}cm | "
            f"Proximity: {'Yes' if reading.proximity_alert else 'No'}"
        )
        
        # Make distance-based decisions
        self.make_distance_decisions(reading)
        
        # Check distance conditions
        self.check_distance_conditions(reading)
    
    def make_distance_decisions(self, reading: DistanceReading):
        """Make real-time decisions based on distance data"""
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
    
    def check_distance_conditions(self, reading: DistanceReading):
        """Check for custom distance conditions and trigger actions"""
        # Example: Alert if very close object (< 10cm)
        if reading.distance > 0 and reading.distance < 10:
            self.logger.warning(f"Very close object detected: {reading.distance:.1f}cm")
    
    def handle_proximity_alert(self):
        """Handle proximity alert"""
        self.logger.info("ALERT: Object proximity detected")
        if self.on_proximity_callback:
            self.on_proximity_callback()