import pytest
from unittest.mock import patch, MagicMock, Mock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

sys.modules['psycopg'] = Mock()
sys.modules['psycopg.rows'] = Mock()

from app.postgres_data_store import PostgreSQLDataStore


class TestPostgreSQLDataStore:

    @patch('app.postgres_data_store.psycopg.connect')
    def test_init_with_database_url(self, mock_connect):
        """Test initialization with database URL."""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        store = PostgreSQLDataStore(database_url='postgresql://test')
        
        assert store.database_url == 'postgresql://test'
        mock_connect.assert_called()

    def test_init_without_database_url_raises_error(self):
        """Test initialization without database URL raises ValueError."""
        with pytest.raises(ValueError, match="Database URL hasn't been provided"):
            PostgreSQLDataStore()

    @patch('app.postgres_data_store.psycopg.connect')
    def test_validate_provider_no_conflict(self, mock_connect):
        """Test provider validation with no conflict."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        store = PostgreSQLDataStore(database_url='postgresql://test')
        result = store.validate_provider('1234567890', 'Dr. Smith')
        
        assert result[store.CONFLICT_KEY] is False

    @patch('app.postgres_data_store.psycopg.connect')
    def test_validate_provider_npi_exists_different_name(self, mock_connect):
        """Test provider validation when NPI exists with different name."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            {'name_normalized': 'dr. jones', 'name': 'Dr. Jones'},
            None
        ]
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        store = PostgreSQLDataStore(database_url='postgresql://test')
        result = store.validate_provider('1234567890', 'Dr. Smith')
        
        assert result[store.CONFLICT_KEY] is True
        assert 'already exists with name' in result[store.ERROR_MESSAGE_KEY]

    @patch('app.postgres_data_store.psycopg.connect')
    def test_validate_patient_no_conflict(self, mock_connect):
        """Test patient validation with no conflict."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        store = PostgreSQLDataStore(database_url='postgresql://test')
        result = store.validate_patient('123456', 'John', 'Doe')
        
        assert result[store.CONFLICT_KEY] is False

    @patch('app.postgres_data_store.psycopg.connect')
    def test_validate_patient_mrn_exists_different_name(self, mock_connect):
        """Test patient validation when MRN exists with different name."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'first_name': 'Jane', 'last_name': 'Smith'}
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        store = PostgreSQLDataStore(database_url='postgresql://test')
        result = store.validate_patient('123456', 'John', 'Doe')
        
        assert result[store.CONFLICT_KEY] is True
        assert 'already exists with name' in result[store.ERROR_MESSAGE_KEY]

    @patch('app.postgres_data_store.psycopg.connect')
    def test_check_duplicate_order_none_exists(self, mock_connect):
        """Test duplicate order check when no duplicate exists."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        store = PostgreSQLDataStore(database_url='postgresql://test')
        result = store.check_duplicate_order('123456', 'Aspirin')
        
        assert result is False

    @patch('app.postgres_data_store.psycopg.connect')
    def test_check_duplicate_order_exists(self, mock_connect):
        """Test duplicate order check when duplicate exists."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        store = PostgreSQLDataStore(database_url='postgresql://test')
        result = store.check_duplicate_order('123456', 'Aspirin')
        
        assert result is True

    @patch('app.postgres_data_store.psycopg.connect')
    def test_add_provider(self, mock_connect):
        """Test adding provider."""
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        store = PostgreSQLDataStore(database_url='postgresql://test')
        store.add_provider('1234567890', 'Dr. Smith')
        
        assert mock_cursor.execute.call_count == 2
        mock_conn.commit.assert_called()

    @patch('app.postgres_data_store.psycopg.connect')
    def test_add_order(self, mock_connect):
        """Test adding order."""
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        store = PostgreSQLDataStore(database_url='postgresql://test')
        order_data = {
            'patient_mrn': '123456',
            'patient_first_name': 'John',
            'patient_last_name': 'Doe',
            'provider_npi': '1234567890',
            'provider_name': 'Dr. Smith',
            'medication': 'Aspirin',
            'primary_diagnosis': 'Hypertension'
        }
        store.add_order(order_data)
        
        assert mock_cursor.execute.call_count == 2
        mock_conn.commit.assert_called()

    @patch('app.postgres_data_store.psycopg.connect')
    def test_get_stats(self, mock_connect):
        """Test getting statistics."""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [(5,), (3,), (2,)]
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        store = PostgreSQLDataStore(database_url='postgresql://test')
        stats = store.get_stats()
        
        assert stats['total_orders'] == 5
        assert stats['total_patients'] == 3
        assert stats['total_providers'] == 2