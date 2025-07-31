#!/usr/bin/env python3
"""
Sound Sensor Receiver
Handles receiving and parsing sound sensor data from Arduino
"""

import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class SoundReading:
    timestamp: int
    sound_level: int
    sound_raw: int
    sound_detected: bool
    received_at: datetime


class SoundSensorReceiver:
    def __init__(self):
        """Initialize the sound sensor receiver"""
        self.logger = logging.getLogger(__name__)
    
    def parse_sound_data(self, data: dict) -> Optional[SoundReading]:
        """Parse sound-related data from Arduino sensor data"""
        try:
            return SoundReading(
                timestamp=data['timestamp'],
                sound_level=data['sound_level'],
                sound_raw=data['sound_raw'],
                sound_detected=data['sound_detected'],
                received_at=datetime.now()
            )
        except KeyError as e:
            self.logger.warning(f"Missing sound data field: {e}")
            return None
    
