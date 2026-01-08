from typing import List, Dict
import psycopg
from psycopg.rows import dict_row
import os
from data_store import DataStore

class PostgreSQLDataStore(DataStore):

    def __init__(self, database_url: str = None):
        self.database_url = database_url
        if not self.database_url:
            raise ValueError("Database URL hasn't been provided.")
        self._init_schema()
    
    def _conn(self):
        # Get database connection
        return psycopg.connect(self.database_url)
    
    def _init_schema(self):
        # Create tables if they don't exist
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS providers (
                        npi VARCHAR(10) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        name_normalized VARCHAR(255) UNIQUE NOT NULL
                    );
                    
                    CREATE TABLE IF NOT EXISTS patients (
                        mrn VARCHAR(6) PRIMARY KEY,
                        first_name VARCHAR(255) NOT NULL,
                        last_name VARCHAR(255) NOT NULL
                    );
                    
                    CREATE TABLE IF NOT EXISTS orders (
                        order_id SERIAL PRIMARY KEY,
                        patient_mrn VARCHAR(6) REFERENCES patients(mrn),
                        patient_first_name VARCHAR(255) NOT NULL,
                        patient_last_name VARCHAR(255) NOT NULL,
                        provider_npi VARCHAR(10) REFERENCES providers(npi),
                        provider_name VARCHAR(255) NOT NULL,
                        medication VARCHAR(255) NOT NULL,
                        primary_diagnosis TEXT NOT NULL,
                        additional_diagnoses TEXT,
                        medication_history TEXT,
                        patient_records TEXT,
                        care_plan TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
    
    def validate_order(self, data: Dict) -> List:
        warnings = []
        
        # Check for duplicate provider with different name or different npi
        provider_check = self.validate_provider(data['provider_npi'], data['provider_name'])
        if provider_check.get(self.CONFLICT_KEY):
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
        normalized = name.lower().strip()
        
        with self._conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                # Check if this NPI already exists with a different name
                cur.execute("SELECT name_normalized FROM providers WHERE npi = %s", (npi,))
                if row := cur.fetchone():
                    if row['name_normalized'] != normalized:
                        return {self.CONFLICT_KEY: True, self.ERROR_MESSAGE_KEY: f'Provider NPI {npi} already exists with name "{row["name"]}"'}
                
                # Check name with different NPI
                cur.execute("SELECT npi FROM providers WHERE name_normalized = %s", (normalized,))
                if row := cur.fetchone():
                    if row['npi'] != npi:
                        return {self.CONFLICT_KEY: True, self.ERROR_MESSAGE_KEY: f'Provider "{name}" already exists with NPI {row["npi"]}. Same provider cannot have multiple NPIs.'}
        
        return {self.CONFLICT_KEY: False}
    
    def add_provider(self, npi: str, name: str):
        """Add provider to database."""

        # Add provider if new
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO providers (npi, name, name_normalized) VALUES (%s, %s, %s) ON CONFLICT (npi) DO NOTHING",
                    (npi, name, name.lower().strip())
                )
                conn.commit()
    
    def validate_patient(self, mrn: str, first_name: str, last_name: str) -> Dict:
        """Validate patient. Returns conflict if exists with different name."""

        # Check if patient with provided mrn already exists with different name details
        with self._conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT first_name, last_name FROM patients WHERE mrn = %s", (mrn,))
                if row := cur.fetchone():
                    if row['first_name'].lower() != first_name.lower() or row['last_name'].lower() != last_name.lower():
                        return {self.CONFLICT_KEY: True, self.ERROR_MESSAGE_KEY: f'Patient MRN {mrn} already exists with name "{row["first_name"]} {row["last_name"]}"'}
        
        return {self.CONFLICT_KEY: False}
    
    def add_patient(self, mrn: str, first_name: str, last_name: str):
        """Add patient to database."""
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO patients (mrn, first_name, last_name) VALUES (%s, %s, %s) ON CONFLICT (mrn) DO NOTHING",
                    (mrn, first_name, last_name)
                )
                conn.commit()
    
    def check_duplicate_order(self, mrn: str, medication: str) -> bool:
        """Check if an identical order already exists."""
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM orders WHERE patient_mrn = %s AND LOWER(medication) = LOWER(%s) LIMIT 1",
                    (mrn, medication)
                )
                return cur.fetchone() is not None
        return False
    
    def add_order(self, order_data: Dict):
        """Add order to database."""
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO orders (
                        patient_mrn, patient_first_name, patient_last_name,
                        provider_npi, provider_name, medication, primary_diagnosis,
                        additional_diagnoses, medication_history, patient_records, care_plan
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    order_data['patient_mrn'], order_data['patient_first_name'], order_data['patient_last_name'],
                    order_data['provider_npi'], order_data['provider_name'], order_data['medication'],
                    order_data['primary_diagnosis'], order_data.get('additional_diagnoses', ''), 
                    order_data.get('medication_history', ''), order_data.get('patient_records', ''), 
                    order_data.get('care_plan', '')
                ))
                conn.commit()
    
    def export_orders(self) -> List[Dict]:
        """Export all orders."""
        with self._conn() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT order_id, patient_mrn, patient_first_name, patient_last_name,
                           provider_npi, provider_name, medication, primary_diagnosis,
                           additional_diagnoses, medication_history, patient_records, 
                           care_plan, timestamp
                    FROM orders ORDER BY timestamp DESC
                """)
                return [dict(row) for row in cur.fetchall()]
    
    def get_stats(self) -> Dict:
        """Get statistics."""
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM orders")
                total_orders = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM patients")
                total_patients = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM providers")
                total_providers = cur.fetchone()[0]
                
                return {
                    'total_orders': total_orders,
                    'total_patients': total_patients,
                    'total_providers': total_providers
                }