from django.test import TestCase

# Create your tests here.
import os
import tempfile
from unittest.mock import MagicMock

# Mock google.genai if not installed, to prevent import errors
try:
    from google import genai
except ImportError:
    genai = MagicMock()

from django.conf import settings

# Ensure settings are configured for the test environment
if not settings.configured:
    settings.configure(
        GEMINI_API_KEY="dummy-key",
        SECRET_KEY="dummy-key",
        DEBUG=True,
        INSTALLED_APPS=['accounts']
    )

from .gemini_service import analyze_id_document

class GeminiServiceTest(TestCase):
    
    def test_api_key_missing(self):
        """
        Test behavior when GEMINI_API_KEY is missing.
        Should return Pending status.
        """
        # Temporarily remove the API key
        original_key = getattr(settings, 'GEMINI_API_KEY', None)
        settings.GEMINI_API_KEY = None
        
        result = analyze_id_document("/fake/path")
        
        # Restore the key
        settings.GEMINI_API_KEY = original_key
        
        self.assertEqual(result[1], 'Pending')
        self.assertIn("Manual review", result[2])

    def test_api_success(self):
        """
        Test successful API interaction (mocked).
        """
        # Create a mock file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(b"fake image data")
            tmp_path = tmp_file.name

        # Mock the genai client and its methods
        mock_genai = MagicMock()
        
        # Mock the file upload
        mock_uploaded_file = MagicMock()
        mock_uploaded_file.name = "files/fake_file_id"
        
        mock_genai.files.upload.return_value = mock_uploaded_file
        
        # Mock the generate_content response
        mock_response = MagicMock()
        mock_response.text = '{"is_valid": true, "reason": "Valid ID"}'
        mock_genai.models.generate_content.return_value = mock_response

        # Replace the actual genai with the mock for this test
        original_genai = genai
        globals()['genai'] = mock_genai

        try:
            result = analyze_id_document(tmp_path)
            
            # Check results
            self.assertEqual(result[0], True)
            self.assertEqual(result[1], 'Approved')
            
            # Check if methods were called correctly
            mock_genai.files.upload.assert_called_once_with(file=tmp_path)
            mock_genai.models.generate_content.assert_called_once()
            mock_genai.files.delete.assert_called_once_with(name="files/fake_file_id")
            
        finally:
            # Cleanup
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            globals()['genai'] = original_genai

    def test_api_failure(self):
        """
        Test failure during API call.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(b"fake image data")
            tmp_path = tmp_file.name

        mock_genai = MagicMock()
        mock_genai.files.upload.side_effect = Exception("API Error")
        
        globals()['genai'] = mock_genai

        try:
            result = analyze_id_document(tmp_path)
            
            self.assertEqual(result[0], False)
            self.assertEqual(result[1], 'Pending')
            self.assertIn("Manual review", result[2])
            
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            globals()['genai'] = genai
            