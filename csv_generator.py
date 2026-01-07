import io
import csv
from typing import List
from flask import send_file
from datetime import datetime

FIELD_NAMES = [
    'order_id', 'timestamp', 'patient_first_name', 'patient_last_name',
    'patient_mrn', 'provider_name', 'provider_npi', 'primary_diagnosis',
    'medication', 'additional_diagnoses', 'medication_history', 
    'patient_records', 'care_plan'
]

class CSVGenerator:
    def __init__(self):
        # Initialize output io and writer
        self.output = io.StringIO()
        self.writer = csv.DictWriter(self.output, fieldnames=FIELD_NAMES)
        self.writer.writeheader()
    
    def write_data(self, orders: List):
        # Write all the data in orders as rows
        for order in orders:
            row = {k: order.get(k, '') for k in FIELD_NAMES}
            self.writer.writerow(row)
    
    def prepare_for_download(self):
        # Prepare and send CSV file for download
        self.output.seek(0)
        return send_file(
            io.BytesIO(self.output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'care_plans_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
