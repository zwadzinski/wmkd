#!/usr/bin/env python3
"""
Distance Sensor Receiver
Handles receiving and parsing distance sensor data from Arduino
"""

import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class DistanceReading:
    timestamp: int
    distance: float
    proximity_alert: bool
    received_at: datetime


class DistanceSensorReceiver:
    def __init__(self):
        """Initialize the distance sensor receiver"""
        self.logger = logging.getLogger(__name__)
    
    def parse_distance_data(self, data: dict) -> Optional[DistanceReading]:
        """Parse distance-related data from Arduino sensor data"""
        try:
            return DistanceReading(
                timestamp=data['timestamp'],
                distance=data['distance'],
                proximity_alert=data['proximity_alert'],
                received_at=datetime.now()
            )
        except KeyError as e:
            self.logger.warning(f"Missing distance data field: {e}")
            return None
    
