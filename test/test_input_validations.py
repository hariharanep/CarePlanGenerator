import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.input_validations import InputHandler

class TestInputHandler:

    def test_parse_additional_diagnoses_with_value(self):
        """Test parsing additional diagnoses with valid input."""
        result = InputHandler.parse_additional_diagnoses("  Diabetes, Hypertension  ")
        assert result == "Diabetes, Hypertension"

    def test_parse_additional_diagnoses_empty(self):
        """Test parsing additional diagnoses with empty input."""
        result = InputHandler.parse_additional_diagnoses("")
        assert result == "No additional diagnoses provided"

    def test_parse_medication_history_with_value(self):
        """Test parsing medication history with valid input."""
        result = InputHandler.parse_medication_history("  Aspirin 81mg daily  ")
        assert result == "Aspirin 81mg daily"

    def test_parse_medication_history_empty(self):
        """Test parsing medication history with empty input."""
        result = InputHandler.parse_medication_history("")
        assert result == "No medication history provided"

    def test_prepare_patient_records_with_value(self):
        """Test parsing patient records with valid input."""
        result = InputHandler.prepare_patient_records("  Lab results attached  ")
        assert result == "Lab results attached"

    def test_prepare_patient_records_empty(self):
        """Test parsing patient records with empty input."""
        result = InputHandler.prepare_patient_records("")
        assert result == "No additional records provided"

    def test_validate_npi_valid(self):
        """Test NPI validation with valid 10-digit NPI."""
        valid, error = InputHandler.validate_npi("1234567890", "Provider NPI")
        assert valid is True
        assert error is None

    def test_validate_npi_invalid_length(self):
        """Test NPI validation with invalid length."""
        valid, error = InputHandler.validate_npi("12345", "Provider NPI")
        assert valid is False
        assert "must be exactly 10 digits" in error

    def test_validate_npi_non_numeric(self):
        """Test NPI validation with non-numeric characters."""
        valid, error = InputHandler.validate_npi("123456789X", "Provider NPI")
        assert valid is False
        assert "must be exactly 10 digits" in error

    def test_validate_mrn_valid(self):
        """Test MRN validation with valid 6-digit MRN."""
        valid, error = InputHandler.validate_mrn("123456", "Patient MRN")
        assert valid is True
        assert error is None

    def test_validate_mrn_invalid_length(self):
        """Test MRN validation with invalid length."""
        valid, error = InputHandler.validate_mrn("12345", "Patient MRN")
        assert valid is False
        assert "must be exactly 6 digits" in error

    def test_validate_required_string_valid(self):
        """Test required string validation with valid input."""
        valid, error = InputHandler.validate_required_string("John", "Patient First Name")
        assert valid is True
        assert error is None

    def test_validate_required_string_empty(self):
        """Test required string validation with empty input."""
        valid, error = InputHandler.validate_required_string("", "Patient First Name")
        assert valid is False
        assert "is required" in error

    def test_sanitize_input_complete_data(self):
        """Test sanitizing input with complete data."""
        data = {
            "patient_first_name": "  John  ",
            "patient_last_name": "  Doe  ",
            "provider_name": "  Dr. Smith  ",
            "provider_npi": "1234567890",
            "patient_mrn": "123456",
            "primary_diagnosis": "  Hypertension  ",
            "medication": "  Lisinopril  ",
            "additional_diagnoses": "  Diabetes  ",
            "medication_history": "  Aspirin  ",
            "patient_records": "  Labs  "
        }
        
        result = InputHandler.sanitize_input(data)
        
        assert result["patient_first_name"] == "John"
        assert result["additional_diagnoses"] == "Diabetes"
        assert result["medication_history"] == "Aspirin"
        assert result["patient_records"] == "Labs"

    def test_validate_input_valid_data(self):
        """Test input validation with valid data."""
        data = {
            "patient_first_name": "John",
            "patient_last_name": "Doe",
            "provider_name": "Dr. Smith",
            "provider_npi": "1234567890",
            "patient_mrn": "123456",
            "primary_diagnosis": "Hypertension",
            "medication": "Lisinopril"
        }
        
        errors = InputHandler.validate_input(data)
        assert errors == []

    def test_validate_input_missing_required_fields(self):
        """Test input validation with missing required fields."""
        data = {
            "patient_first_name": "",
            "provider_npi": "123",
            "patient_mrn": "12345"
        }
        
        errors = InputHandler.validate_input(data)
        assert len(errors) > 0
        assert any("is required" in error for error in errors)

    def test_validate_input_invalid_npi_and_mrn(self):
        """Test input validation with invalid NPI and MRN."""
        data = {
            "patient_first_name": "John",
            "patient_last_name": "Doe",
            "provider_name": "Dr. Smith",
            "provider_npi": "123",
            "patient_mrn": "12345",
            "primary_diagnosis": "Hypertension",
            "medication": "Lisinopril"
        }
        
        errors = InputHandler.validate_input(data)
        assert len(errors) == 2
        assert any("10 digits" in error for error in errors)
        assert any("6 digits" in error for error in errors)