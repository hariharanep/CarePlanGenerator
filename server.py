from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from typing import Dict
from app.input_validations import InputHandler
from app.in_memory_data_store import InMemoryDataStore
from app.postgres_data_store import PostgreSQLDataStore
from app.care_plan_generator import CarePlanGenerator
from app.csv_generator import CSVGenerator
from app.data_store import DataStore

load_dotenv()
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
input_handler = InputHandler()

def create_store() -> DataStore:
    database_url = os.environ.get('DATABASE_URL')
    if os.environ.get('DATABASE_URL'):
        return PostgreSQLDataStore(database_url)
    return InMemoryDataStore()

store = create_store()

@app.route('/')
def index():
    """Render the main form."""
    return render_template('index.html')

def validate_order_data(data: Dict):
    # sanitize input
    sanitized_data = input_handler.sanitize_input(data)

    # If basic input validation fails, return error response
    input_errors = input_handler.validate_input(sanitized_data)
    if input_errors:
        return False, input_errors, sanitized_data

    # If order validation fails, return error response
    order_warnings = store.validate_order(sanitized_data)
    if order_warnings:
        return True, order_warnings, sanitized_data

    # If validation passes, return sanitized input
    return True, None, sanitized_data

@app.route('/care-plan/validate', methods=['POST'])
def validate_order():
    """Validate order data."""
    try:
        data = request.json

        # validate data
        valid, validations, sanitized_data = validate_order_data(data)

        # If validation errors exist return error response
        if not valid: 
            return jsonify({
                'errors': validations
            }), 400
        
        # Return success response along with warnings
        return jsonify({
            'sanitized_data': sanitized_data, 
            'warnings': validations
        }), 200
    except Exception as e:
        return jsonify({
            'errors': ["Validation request failed due to an internal error."]
        }), 500

@app.route('/care-plan/generate', methods=['POST'])
def generate_care_plan():
    """Generate care plan using LLM."""
    try:
        data = request.json
        
        # Generate care plan using LLM
        care_plan_generator = CarePlanGenerator()
        care_plan = care_plan_generator.generate_care_plan_with_llm(data)
        
        # Return the full order with the generated care plan
        data["care_plan"] = care_plan
        return jsonify({
            'full_order': data,
        }), 200
        
    except Exception as e:
        return jsonify({
            'errors': ['Failed to generate care plan due to an internal error.']
        }), 500

@app.route('/care-plan/submit', methods=['POST'])
def submit_order():
    """Persist Full Validated Order with Care Plan in Internal Data Storage."""
    try:
        data = request.json

        # Persist the patient data
        store.add_patient(
            data['patient_mrn'],
            data['patient_first_name'],
            data['patient_last_name']
        )

        # Persist the provider data
        store.add_provider(
            data['provider_npi'],
            data['provider_name']
        )

        # Persist the order data
        store.add_order(data)
        
        # Return the full order in the response
        return jsonify({
            'full_order': data,
        }), 200
        
    except Exception as e:
        return jsonify({
            'errors': ['Failed to persist order due to an internal error.'],
        }), 500

@app.route('/care-plan/orders', methods=['GET'])
def export_orders():
    """Export all orders to a CSV file."""
    try:
        # Retrieve all persisted orders
        orders = store.export_orders()
        
        # If no orders exist in internal data storage return Not Found response
        if not orders:
            return jsonify({'error': 'No orders to export'}), 404

        csv_generator = CSVGenerator()
        
        # Write orders to a csv file
        csv_generator.write_data(orders)

        # Return newly created csv file as response
        return csv_generator.prepare_for_download()
    except Exception as e:
        return jsonify({'error': 'Export failed due to an internal error'}), 500

@app.route('/care-plan/stats', methods=['GET'])
def get_stats():
    """Get statistics about stored data."""
    response = jsonify(store.get_stats())

    # Prevent caching of stats
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)