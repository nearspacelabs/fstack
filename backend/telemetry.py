import json
import random
from datetime import datetime, timedelta
import os
import math

class TelemetrySimulator:
    def __init__(self):
        self.current_index = 0
        self.delayed_points = []
        self.last_timestamp = datetime.now()
        self.points = self._load_trajectory()
        self.sent_points = set()  # Track points we've already sent
        self.max_altitude = 5000  # Maximum altitude in meters
        self.min_altitude = 100   # Minimum altitude in meters
        
    def _load_trajectory(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        trajectory_path = os.path.join(current_dir, 'trajectory.json')
        
        with open(trajectory_path, 'r') as f:
            data = json.load(f)
            coordinates = data['features'][0]['geometry']['coordinates']
            return coordinates

    def _generate_altitude(self):
        """
        Generate altitude based on the current position in the trajectory:
        - First 20%: Ascending phase
        - Middle 60%: Cruise phase with small variations
        - Last 20%: Descending phase
        """
        total_points = len(self.points)
        progress = self.current_index / total_points

        # Add some noise to make it more realistic
        noise = random.uniform(-50, 50)

        if progress < 0.2:  # Ascending phase
            # Quadratic ascent for smoother takeoff
            altitude = self.min_altitude + (self.max_altitude - self.min_altitude) * (progress / 0.2) ** 2
        elif progress > 0.8:  # Descending phase
            # Remaining progress from 0.8 to 1.0 (normalized to 0-1)
            descent_progress = (progress - 0.8) / 0.2
            # Inverse quadratic for smooth landing
            altitude = self.max_altitude * (1 - descent_progress ** 2)
            if altitude < self.min_altitude:
                altitude = self.min_altitude
        else:  # Cruise phase
            # Small variations during cruise
            variation = math.sin(progress * 10) * 200  # Gentle wave pattern
            altitude = self.max_altitude + variation

        return altitude + noise

    def _should_delay_point(self):
        """30% chance to delay a point"""
        return random.random() < 0.3

    def _create_telemetry_point(self, coord, timestamp):
        """Create a telemetry point with longitude, latitude, altitude, and timestamp"""
        return {
            "longitude": coord[0],
            "latitude": coord[1],
            "altitude": self._generate_altitude(),
            "timestamp": timestamp.isoformat()
        }

    def get_telemetry(self):
        """
        Returns 1-3 telemetry points, possibly including delayed points from earlier
        in the trajectory.
        """
        if self.current_index >= len(self.points):
            self.current_index = 0  # Reset to create a loop
            self.sent_points.clear()
            self.delayed_points.clear()
            self.last_timestamp = datetime.now()

        num_points = random.randint(1, 3)
        telemetry_points = []
        
        # First, randomly include some delayed points
        if self.delayed_points and random.random() < 0.4:  # 40% chance to include delayed points
            num_delayed = random.randint(1, min(2, len(self.delayed_points)))
            for _ in range(num_delayed):
                if self.delayed_points:
                    telemetry_points.append(self.delayed_points.pop(0))
                    num_points -= 1

        # Then add new points
        for _ in range(num_points):
            if self.current_index >= len(self.points):
                break

            current_point = self.points[self.current_index]
            
            # Generate timestamp that's 2-5 seconds after the last one
            self.last_timestamp += timedelta(seconds=random.uniform(2, 5))
            
            if self._should_delay_point() and self.current_index < len(self.points) - 1:
                # Store point for later with its timestamp
                self.delayed_points.append(
                    self._create_telemetry_point(current_point, self.last_timestamp)
                )
            else:
                telemetry_points.append(
                    self._create_telemetry_point(current_point, self.last_timestamp)
                )
            
            self.current_index += 1

        # Sort points by timestamp before returning
        return sorted(telemetry_points, key=lambda x: x['timestamp'])

# Create a singleton instance
telemetry_simulator = TelemetrySimulator()

def get_telemetry():
    """
    Public function to get telemetry data.
    Returns 1-3 points with their coordinates, altitude, and timestamps.
    Some points might be delayed and returned in later calls.
    """
    return telemetry_simulator.get_telemetry()

