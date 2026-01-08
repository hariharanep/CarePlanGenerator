import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.care_plan_generator import CarePlanGenerator

class TestCarePlanGenerator:

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        generator = CarePlanGenerator()
        assert generator.client is not None

    @patch.dict('os.environ', {}, clear=True)
    def test_init_without_api_key_raises_error(self):
        """Test initialization without API key raises ValueError."""
        with pytest.raises(ValueError, match="API Key hasn't been provided"):
            CarePlanGenerator()

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('app.care_plan_generator.generate_prompt')
    def test_generate_care_plan_success(self, mock_prompt):
        """Test successful care plan generation."""
        # Setup
        mock_prompt.return_value = "test prompt"
        generator = CarePlanGenerator()
        
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Generated care plan")]
        generator.client.messages.create = MagicMock(return_value=mock_response)
        
        # Execute
        result = generator.generate_care_plan_with_llm({"patient": "data"})
        
        # Assert
        assert result == "Generated care plan"
        mock_prompt.assert_called_once_with({"patient": "data"})
        generator.client.messages.create.assert_called_once()

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('app.care_plan_generator.generate_prompt')
    def test_generate_care_plan_api_failure(self, mock_prompt):
        """Test API failure raises RuntimeError."""
        # Setup
        mock_prompt.return_value = "test prompt"
        generator = CarePlanGenerator()
        generator.client.messages.create = MagicMock(side_effect=Exception("API Error"))
        
        # Execute & Assert
        with pytest.raises(RuntimeError, match="LLM call failed to return a valid response"):
            generator.generate_care_plan_with_llm({"patient": "data"})