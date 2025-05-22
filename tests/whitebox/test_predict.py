# tests/whitebox/test_predict_integration.py
import sys, os
# go up two levels to the project root
root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, root)
import os
import io
import unittest

from app import app

class PredictIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # ensure we're in testing mode
        app.config['TESTING'] = True
        cls.client = app.test_client()

        # path to our fixture
        cls.fixture_dir = os.path.join(
            os.path.dirname(__file__), 
            'fixtures'
        )
        if not os.path.isdir(cls.fixture_dir):
            raise RuntimeError(
                f"Please create a directory {cls.fixture_dir} "
                "and add a known-sick image named 'sick1.jpg'."
            )
    def _post_image(self, filename):
        """Helper to POST a fixture image and return the JSON response."""
        path = os.path.join(self.fixture_dir, filename)
        with open(path, 'rb') as f:
            data = {'file': (io.BytesIO(f.read()), filename)}
            resp = self.client.post(
                '/predict',
                data=data,
                content_type='multipart/form-data'
            )
        return resp
    
    def test_known_sick_image(self):
        img_path = os.path.join(self.fixture_dir, 'sick1.jpg')
        with open(img_path, 'rb') as img:
            data = {
                'file': (io.BytesIO(img.read()), 'sick1.jpg')
            }
            resp = self.client.post(
                '/predict',
                data=data,
                content_type='multipart/form-data'
            )
        # we expect a 200 OK and a 'Sick' result
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        js = resp.get_json()
        self.assertEqual(js.get('result'), 'Sick',
                         f"Expected 'Sick', got {js!r}")

    def test_known_healthy_image(self):
        img_path = os.path.join(self.fixture_dir, 'healthy1.jpg')
        with open(img_path, 'rb') as img:
            data = {
                'file': (io.BytesIO(img.read()), 'healthy1.jpg')
            }
            resp = self.client.post(
                '/predict',
                data=data,
                content_type='multipart/form-data'
            )
        # Expect HTTP 200 and a "Healthy" result
        self.assertEqual(resp.status_code, 200, resp.get_data(as_text=True))
        js = resp.get_json()
        self.assertEqual(js.get('result'), 'Healthy',
                         f"Expected 'Healthy', got {js!r}")

if __name__ == '__main__':
    unittest.main()
