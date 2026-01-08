import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.csv_generator import CSVGenerator

class TestCSVGenerator:

    def test_init_creates_header(self):
        """Test initialization creates CSV with header."""
        generator = CSVGenerator()
        
        output = generator.output.getvalue()
        assert 'order_id' in output
        assert 'patient_first_name' in output
        assert 'care_plan' in output

    def test_write_data_single_order(self):
        """Test writing single order to CSV."""
        generator = CSVGenerator()
        
        orders = [{'order_id': '123', 'patient_first_name': 'John', 'patient_last_name': 'Doe'}]
        generator.write_data(orders)
        
        output = generator.output.getvalue()
        assert '123' in output
        assert 'John' in output
        assert 'Doe' in output

    def test_write_data_multiple_orders(self):
        """Test writing multiple orders to CSV."""
        generator = CSVGenerator()
        
        orders = [
            {'order_id': '123', 'patient_first_name': 'John'},
            {'order_id': '456', 'patient_first_name': 'Jane'}
        ]
        generator.write_data(orders)
        
        output = generator.output.getvalue()
        lines = output.strip().split('\n')
        assert len(lines) == 3 

    @patch('app.csv_generator.send_file')
    @patch('app.csv_generator.datetime')
    def test_prepare_for_download(self, mock_datetime, mock_send_file):
        """Test CSV file preparation for download."""
        mock_datetime.now.return_value.strftime.return_value = '20250108_120000'
        mock_send_file.return_value = MagicMock()
        
        generator = CSVGenerator()
        generator.write_data([{'order_id': '123'}])
        
        result = generator.prepare_for_download()
        
        mock_send_file.assert_called_once()
        call_kwargs = mock_send_file.call_args[1]
        assert call_kwargs['mimetype'] == 'text/csv'
        assert call_kwargs['as_attachment'] is True
        assert 'care_plans_export_20250108_120000.csv' in call_kwargs['download_name']