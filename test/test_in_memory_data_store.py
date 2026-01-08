import pytest
from unittest.mock import patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.in_memory_data_store import InMemoryDataStore

class TestInMemoryDataStore:

    def test_init(self):
        """Test initialization."""
        store = InMemoryDataStore()
        assert store.providers == {}
        assert store.patients == {}
        assert store.orders == []

    def test_validate_provider_no_conflict(self):
        """Test provider validation with no conflict."""
        store = InMemoryDataStore()
        result = store.validate_provider('123', 'Dr. Smith')
        assert result['conflict'] is False

    def test_validate_provider_npi_exists_different_name(self):
        """Test provider validation when NPI exists with different name."""
        store = InMemoryDataStore()
        store.add_provider('123', 'Dr. Smith')
        
        result = store.validate_provider('123', 'Dr. Jones')
        assert result['conflict'] is True
        assert 'already exists with name' in result[store.ERROR_MESSAGE_KEY]

    def test_validate_provider_name_exists_different_npi(self):
        """Test provider validation when name exists with different NPI."""
        store = InMemoryDataStore()
        store.add_provider('123', 'Dr. Smith')
        
        result = store.validate_provider('456', 'Dr. Smith')
        assert result['conflict'] is True
        assert 'already exists with NPI' in result[store.ERROR_MESSAGE_KEY]

    def test_validate_patient_no_conflict(self):
        """Test patient validation with no conflict."""
        store = InMemoryDataStore()
        result = store.validate_patient('MRN123', 'John', 'Doe')
        assert result['conflict'] is False

    def test_validate_patient_mrn_exists_different_name(self):
        """Test patient validation when MRN exists with different name."""
        store = InMemoryDataStore()
        store.add_patient('MRN123', 'John', 'Doe')
        
        result = store.validate_patient('MRN123', 'Jane', 'Smith')
        assert result['conflict'] is True
        assert 'already exists with name' in result[store.ERROR_MESSAGE_KEY]

    def test_check_duplicate_order_none_exists(self):
        """Test duplicate order check when no duplicate exists."""
        store = InMemoryDataStore()
        result = store.check_duplicate_order('MRN123', 'Aspirin')
        assert result is False

    def test_check_duplicate_order_exists(self):
        """Test duplicate order check when duplicate exists."""
        store = InMemoryDataStore()
        store.add_order({'patient_mrn': 'MRN123', 'medication': 'Aspirin'})
        
        result = store.check_duplicate_order('MRN123', 'Aspirin')
        assert result is True

    def test_validate_order_no_warnings(self):
        """Test order validation with no warnings."""
        store = InMemoryDataStore()
        data = {
            'provider_npi': '123',
            'provider_name': 'Dr. Smith',
            'patient_mrn': 'MRN123',
            'patient_first_name': 'John',
            'patient_last_name': 'Doe',
            'medication': 'Aspirin'
        }
        
        warnings = store.validate_order(data)
        assert warnings == []

    def test_validate_order_with_warnings(self):
        """Test order validation with multiple warnings."""
        store = InMemoryDataStore()
        store.add_provider('123', 'Dr. Smith')
        store.add_patient('MRN123', 'John', 'Doe')
        store.add_order({'patient_mrn': 'MRN123', 'medication': 'Aspirin'})
        
        data = {
            'provider_npi': '123',
            'provider_name': 'Dr. Jones',  # Different name
            'patient_mrn': 'MRN123',
            'patient_first_name': 'Jane',  # Different name
            'patient_last_name': 'Smith',
            'medication': 'Aspirin'  # Duplicate
        }
        
        warnings = store.validate_order(data)
        assert len(warnings) == 3

    @patch('app.in_memory_data_store.datetime')
    def test_add_order(self, mock_datetime):
        """Test adding order."""
        mock_datetime.now.return_value.isoformat.return_value = '2025-01-08T12:00:00'
        store = InMemoryDataStore()
        
        order_data = {'patient_mrn': 'MRN123', 'medication': 'Aspirin'}
        store.add_order(order_data)
        
        assert len(store.orders) == 1
        assert store.orders[0]['order_id'] == 1
        assert store.orders[0]['timestamp'] == '2025-01-08T12:00:00'

    def test_export_orders(self):
        """Test exporting orders."""
        store = InMemoryDataStore()
        store.add_order({'patient_mrn': 'MRN123'})
        store.add_order({'patient_mrn': 'MRN456'})
        
        orders = store.export_orders()
        assert len(orders) == 2

    def test_get_stats(self):
        """Test getting statistics."""
        store = InMemoryDataStore()
        store.add_provider('123', 'Dr. Smith')
        store.add_patient('MRN123', 'John', 'Doe')
        store.add_order({'patient_mrn': 'MRN123'})
        
        stats = store.get_stats()
        assert stats['total_orders'] == 1
        assert stats['total_patients'] == 1
        assert stats['total_providers'] == 1