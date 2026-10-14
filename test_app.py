import unittest
import json
import io
from app import app
from services.database import init_db, query_db

class WomenSafetyTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret'
        self.client = app.test_client()
        with app.app_context():
            init_db()

    def test_01_home_page_loads(self):
        """Test landing / login page loads successfully."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SafePass', response.data)

    def test_02_user_login(self):
        """Test user login with seeded demo account."""
        response = self.client.post('/login', data={
            'email': 'priya@example.com',
            'password': 'demo123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Emergency Distress Assistance', response.data)

    def test_03_admin_login(self):
        """Test admin login and access to cloud admin dashboard."""
        response = self.client.post('/login', data={
            'email': 'admin@cloudsafety.org',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AWS Cloud Administration', response.data)
        self.assertIn(b'Amazon EC2', response.data)

    def test_04_api_routes(self):
        """Test safe route alternatives calculation API."""
        payload = {
            'origin_lat': 13.0827,
            'origin_lng': 80.2707,
            'dest_lat': 13.0475,
            'dest_lng': 80.2090
        }
        response = self.client.post('/api/routes',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertGreaterEqual(len(data['routes']), 2)
        # Verify safety score is attached
        self.assertIn('safety', data['routes'][0])
        self.assertIn('score', data['routes'][0]['safety'])

    def test_05_api_sos_trigger(self):
        """Test emergency SOS dispatch API."""
        payload = {
            'latitude': 13.0827,
            'longitude': 80.2707,
            'address': 'Test Metro Station'
        }
        response = self.client.post('/api/sos',
                                    data=json.dumps(payload),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['alert']['status'], 'triggered')
        self.assertIn('google.com/maps', data['alert']['maps_url'])

    def test_06_report_submission_local(self):
        """Test submitting a community safety report with an uploaded image."""
        # Log in first
        self.client.post('/login', data={'email': 'priya@example.com', 'password': 'demo123'})
        
        # Fake test image
        img_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        data = {
            'title': 'Dark Corner near Bus Stop',
            'category': 'poorly_lit',
            'severity': 'high',
            'description': 'Streetlight has been off for 3 days.',
            'latitude': '13.0830',
            'longitude': '80.2710',
            'incident_image': (io.BytesIO(img_bytes), 'evidence.png')
        }
        response = self.client.post('/reports', data=data, content_type='multipart/form-data', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dark Corner near Bus Stop', response.data)

if __name__ == '__main__':
    unittest.main()
