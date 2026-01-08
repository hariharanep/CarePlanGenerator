from typing import Optional, Dict, List, Tuple
import re

class InputHandler:

    REQUIRED_FIELDS = ["patient_first_name", "patient_last_name", "provider_name", 
                       "provider_npi", "patient_mrn", "primary_diagnosis", "medication"]

    FIELD_TO_LABEL_MAP = {
        "patient_first_name": "Patient First Name",
        "patient_last_name": "Patient Last Name",
        "provider_name": "Provider Name",
        "provider_npi": "Provider NPI",
        "patient_mrn": "Patient MRN",
        "primary_diagnosis": "Primary Diagnosis",
        "medication": "Medication",
        "additional_diagnoses": "Additional Diagnoses",
        "medication_history": "Medication History",
        "patient_records": "Patient Records"
    }

    UNKNOWN_FIELD = "Unknown Field"
    EMPTY_STRING = ""

    @staticmethod
    def parse_additional_diagnoses(additional_dx_raw: str) -> List:
        """Parse Additional Diagnoses Field"""

        # Parse additional diagnoses into a string with no leading or trailing spaces
        additional_dx = ''
        if isinstance(additional_dx_raw, str):
            additional_dx = additional_dx_raw.strip()
        return additional_dx if additional_dx else 'No additional diagnoses provided'

    @staticmethod
    def parse_medication_history(medication_history_raw: str) -> str:
        """Parse Medication History Field"""

        # Parse medication history into a string with no leading or trailing spaces
        medication_history = ''
        if isinstance(medication_history_raw, str):
            medication_history = medication_history_raw.strip()
        return medication_history if medication_history else 'No medication history provided'

    @staticmethod
    def prepare_patient_records(patient_records_raw: str) -> str:
        """Parse Patient Records Field"""

        # Parse patient records into a string with no leading or trailing spaces
        patient_records = ''
        if isinstance(patient_records_raw, str):
            patient_records = patient_records_raw.strip()
        return patient_records if patient_records else 'No additional records provided'
    
    @staticmethod
    def sanitize_input(data: Dict) -> Dict:
        sanitized_data = {}

        # Sanitize fields that aren't required
        sanitized_data["additional_diagnoses"] = InputHandler.parse_additional_diagnoses(data.get("additional_diagnoses", InputHandler.EMPTY_STRING))
        sanitized_data["medication_history"] = InputHandler.parse_medication_history(data.get("medication_history", InputHandler.EMPTY_STRING))
        sanitized_data["patient_records"] = InputHandler.prepare_patient_records(data.get("patient_records", InputHandler.EMPTY_STRING))

        # Sanitize required fields
        for field in InputHandler.REQUIRED_FIELDS:
            raw_field_value = data.get(field, InputHandler.EMPTY_STRING)
            if isinstance(raw_field_value, str):
                sanitized_data[field] = raw_field_value.strip()        
        return sanitized_data

    @staticmethod
    def validate_input(data: Dict):
        errors = []

        # Validate required fields
        for field in InputHandler.REQUIRED_FIELDS:
            valid, error = InputHandler.validate_required_string(data.get(field, InputHandler.EMPTY_STRING), InputHandler.FIELD_TO_LABEL_MAP.get(field, field))
            if not valid:
                errors.append(error)
        
        # Validate provider npi
        valid, error = InputHandler.validate_npi(data.get('provider_npi', InputHandler.EMPTY_STRING), InputHandler.FIELD_TO_LABEL_MAP.get("provider_npi", InputHandler.UNKNOWN_FIELD))
        if not valid:
            errors.append(error)

        # Validate patient mrn 
        valid, error = InputHandler.validate_mrn(data.get('patient_mrn', InputHandler.EMPTY_STRING), InputHandler.FIELD_TO_LABEL_MAP.get("patient_mrn", InputHandler.UNKNOWN_FIELD))
        if not valid:
            errors.append(error)
        
        # Return all input validation errors
        return errors

    @staticmethod
    def validate_npi(npi: str, field_name: str) -> Tuple[bool, Optional[str]]:
        """Validate NPI is exactly 10 digits."""
        if not re.match(r'^\d{10}$', npi):
            return False, f"{field_name} must be exactly 10 digits"
        return True, None

    @staticmethod
    def validate_mrn(mrn: str, field_name: str) -> Tuple[bool, Optional[str]]:
        """Validate MRN is exactly 6 digits."""
        if not re.match(r'^\d{6}$', mrn):
            return False, f"{field_name} must be exactly 6 digits"
        return True, None

    @staticmethod
    def validate_required_string(value: str, field_name: str) -> Tuple[bool, Optional[str]]:
        """Validate required string field."""
        if not value or not value.strip():
            return False, f"{field_name} is required"
        return True, None        