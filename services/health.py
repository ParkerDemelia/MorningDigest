import os
import json
import glob
from datetime import datetime

class HealthService:
    def __init__(self, health_data_path):
        """health_data_path should be the directory containing the export files"""
        self.data_dir = health_data_path

    def _get_latest_export_file(self):
        # Find all health export files in the directory
        pattern = os.path.join(self.data_dir, "HealthAutoExport-*.json")
        files = glob.glob(pattern)
        
        if not files:
            return None
            
        # Sort by modification time to get the most recent
        return max(files, key=os.path.getmtime)

    def _find_metric(self, data, metric_name):
        for metric in data['data']['metrics']:
            if metric['name'] == metric_name and metric['data']:
                return metric['data'][0]['qty']
        return 'N/A'

    def get_daily_summary(self):
        try:
            latest_file = self._get_latest_export_file()
            if not latest_file:
                return """
                    <li>No health export files found</li>
                    <li>1. Install Health Auto Export from App Store</li>
                    <li>2. Export to the configured directory</li>
                """

            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            # Extract metrics from the correct JSON structure
            steps = self._find_metric(data, 'step_count')
            active_energy = self._find_metric(data, 'active_energy')
            distance = self._find_metric(data, 'walking_running_distance')
            
            return f"""
                <li>🦶 Steps: {int(steps):,}</li>
                <li>🔥 Active Energy: {int(active_energy)} kcal</li>
                <li>🏃 Distance: {distance:.2f} mi</li>
            """
        except Exception as e:
            return f"<li>Unable to read health data: {str(e)}</li>" 