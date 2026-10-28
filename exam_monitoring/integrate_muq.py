"""
Exam Monitoring System - MUQ Integration
Integrate exam monitoring with MUQ backend system
"""

import yaml
import requests
from pathlib import Path
import json
import argparse


class MUQExamMonitor:
    """Integration between Exam Monitoring and MUQ System"""

    def __init__(self, config_path, muq_api_url):
        """Initialize MUQ integration"""
        self.config = self.load_config(config_path)
        self.muq_api_url = muq_api_url.rstrip('/')
        self.api_token = None

    def load_config(self, config_path):
        """Load configuration from YAML file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def authenticate(self, username, password):
        """Authenticate with MUQ API"""
        try:
            response = requests.post(
                f"{self.muq_api_url}/api/login/",
                json={'username': username, 'password': password}
            )

            if response.status_code == 200:
                data = response.json()
                self.api_token = data.get('access')
                print("✅ Successfully authenticated with MUQ API")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error authenticating: {e}")
            return False

    def get_headers(self):
        """Get headers with authentication token"""
        return {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }

    def report_cheating_event(self, event_data):
        """Report cheating event to MUQ system"""
        try:
            response = requests.post(
                f"{self.muq_api_url}/api/exam/cheating-events/",
                headers=self.get_headers(),
                json=event_data
            )

            if response.status_code == 201:
                print("✅ Cheating event reported successfully")
                return response.json()
            else:
                print(f"❌ Failed to report event: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error reporting event: {e}")
            return None

    def get_students_in_exam(self, exam_id):
        """Get list of students registered for an exam"""
        try:
            response = requests.get(
                f"{self.muq_api_url}/api/exam/{exam_id}/students/",
                headers=self.get_headers()
            )

            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get students: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting students: {e}")
            return []

    def update_student_status(self, student_id, status, notes=None):
        """Update student exam status"""
        try:
            data = {'status': status}
            if notes:
                data['notes'] = notes

            response = requests.patch(
                f"{self.muq_api_url}/api/students/{student_id}/",
                headers=self.get_headers(),
                json=data
            )

            if response.status_code == 200:
                print(f"✅ Student {student_id} status updated to {status}")
                return True
            else:
                print(f"❌ Failed to update status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error updating status: {e}")
            return False

    def process_exam_image(self, image_path, exam_id):
        """Process exam image and report to MUQ"""
        from predict import ExamMonitor

        # Initialize exam monitor
        monitor = ExamMonitor(self.config['config'])
        result = monitor.process_image(image_path, save_output=False)

        if not result:
            return None

        analysis = result['analysis']
        cheating = result['cheating']

        # Report to MUQ if cheating detected
        if cheating:
            for event in cheating:
                event_data = {
                    'exam_id': exam_id,
                    'event_type': event['type'],
                    'severity': event['severity'],
                    'details': {
                        'persons_detected': analysis['persons'],
                        'phones_detected': analysis['phones'],
                        'laptops_detected': analysis['laptops'],
                        'timestamp': image_path.stat().st_mtime
                    }
                }

                # Upload image evidence
                # TODO: Implement image upload to MUQ media

                # Report event
                self.report_cheating_event(event_data)

        return result


def main():
    parser = argparse.ArgumentParser(description='Integrate Exam Monitoring with MUQ')
    parser.add_argument('--config', type=str, default='config.yaml',
                        help='Path to configuration file')
    parser.add_argument('--api-url', type=str, required=True,
                        help='MUQ API URL (e.g., http://localhost:8000/api)')
    parser.add_argument('--username', type=str, required=True,
                        help='MUQ username')
    parser.add_argument('--password', type=str, required=True,
                        help='MUQ password')
    parser.add_argument('--image', type=str, required=True,
                        help='Path to exam image')
    parser.add_argument('--exam-id', type=int, required=True,
                        help='Exam ID in MUQ system')
    args = parser.parse_args()

    # Initialize integration
    monitor = MUQExamMonitor(args.config, args.api_url)

    # Authenticate
    if not monitor.authenticate(args.username, args.password):
        print("Authentication failed. Exiting.")
        return

    # Process image
    result = monitor.process_exam_image(Path(args.image), args.exam_id)

    if result:
        print("\nImage processed and reported to MUQ system")
    else:
        print("\nFailed to process image")


if __name__ == '__main__':
    main()
