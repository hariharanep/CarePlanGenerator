from typing import List, Dict
from datetime import datetime
from data_store import DataStore

class InMemoryDataStore(DataStore):
    def __init__(self):
        self.providers = {}  # NPI -> Provider
        self.provider_names = {}  # Normalized provider name -> NPI
        self.patients = {}   # MRN -> Patient
        self.orders = []     # List of orders
    
    def validate_order(self, data: Dict) -> List:
        warnings = []

        # Check for duplicate provider with different name or different npi
        provider_check = self.validate_provider(data['provider_npi'], data['provider_name'])
        if provider_check.get(self.CONFLICT_KEY, False):
            warnings.append(provider_check.get(self.ERROR_MESSAGE_KEY, "Provider Input Error"))
        
        # Check for duplicate patient
        patient_check = self.validate_patient(
            data['patient_mrn'],
            data['patient_first_name'],
            data['patient_last_name']
        )
        if patient_check.get(self.CONFLICT_KEY, False):
            warnings.append(patient_check.get(self.ERROR_MESSAGE_KEY, "Patient Input Error"))
        
        # Check for duplicate order
        if self.check_duplicate_order(
            data['patient_mrn'],
            data['medication'],
        ):
            warnings.append(
                f"A similar order already exists for patient {data['patient_mrn']} "
                f"with medication {data['medication']}"
            )
        
        # Return all the validation warnings that exist
        return warnings
    
    def validate_provider(self, npi: str, name: str) -> Dict:
        """Validate provider. Returns conflict if exists with different name or NPI."""
        normalized_name = name.lower().strip()
        
        # Check if this NPI already exists with a different name
        if npi in self.providers:
            existing = self.providers[npi]
            existing_name = existing.get('name', "")
            if existing_name.lower() != normalized_name:
                return {
                    self.CONFLICT_KEY: True,
                    self.ERROR_MESSAGE_KEY: f'Provider NPI {npi} already exists with name "{existing["name"]}"'
                }
        
        # Check if this provider name already exists with a different NPI
        if normalized_name in self.provider_names:
            existing_npi = self.provider_names[normalized_name]
            if existing_npi != npi:
                return {
                    self.CONFLICT_KEY: True,
                    self.ERROR_MESSAGE_KEY: f'Provider "{name}" already exists with NPI {existing_npi}. Same provider cannot have multiple NPIs.'
                }
            
        return {self.CONFLICT_KEY: False}
        
    def add_provider(self, npi: str, name: str) -> Dict:
        """Add provider."""
        
        # Add provider if new
        if npi not in self.providers:
            normalized_name = name.lower().strip()
            self.providers[npi] = {'npi': npi, 'name': name}
            self.provider_names[normalized_name] = npi
    
    def validate_patient(self, mrn: str, first_name: str, last_name: str) -> Dict:
        """Validate patient. Returns conflict if exists with different name."""

        # Check if patient with provided mrn already exists with different name details
        if mrn in self.patients:
            existing = self.patients[mrn]
            if (existing.get('first_name', "").lower() != first_name.lower() or 
                existing.get('last_name', "").lower() != last_name.lower()):
                return {
                    self.CONFLICT_KEY: True,
                    self.ERROR_MESSAGE_KEY: f'Patient MRN {mrn} already exists with name "{existing["first_name"]} {existing["last_name"]}"'
                }
        return {self.CONFLICT_KEY: False}
                
    def add_patient(self, mrn: str, first_name: str, last_name: str) -> Dict:
        """Add patient."""
        self.patients[mrn] = {
            'mrn': mrn,
            'first_name': first_name,
            'last_name': last_name
        }
    
    def check_duplicate_order(self, mrn: str, medication: str) -> bool:
        """Check if an identical order already exists."""
        for order in self.orders:
            if (order.get('patient_mrn', "") == mrn and 
                order.get('medication', "").lower() == medication.lower()):
                return True
        return False
    
    def add_order(self, order_data: Dict):
        """Add order to storage."""
        order_data['timestamp'] = datetime.now().isoformat()
        order_data['order_id'] = len(self.orders) + 1
        self.orders.append(order_data)
    
    def export_orders(self) -> List[Dict]:
        """Export all orders."""
        return self.orders

    def get_stats(self) -> Dict:
        """Get statistics."""
        
        return {
            'total_orders': len(self.orders),
            'total_patients': len(self.patients),
            'total_providers': len(self.providers)
        }