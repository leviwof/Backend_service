import json
import os
from flask import Flask, jsonify, request

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'customers.json')


def load_customers():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200


@app.route('/api/customers', methods=['GET'])
def get_customers():
    customers = load_customers()
    
    if not customers:
        return jsonify({"error": "No customer data available"}), 500
    
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    if page < 1:
        page = 1
    if limit < 1:
        limit = 10
    if limit > 100:
        limit = 100
    
    total = len(customers)
    start = (page - 1) * limit
    end = start + limit
    
    paginated_data = customers[start:end]
    
    return jsonify({
        "data": paginated_data,
        "total": total,
        "page": page,
        "limit": limit
    }), 200


@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer_by_id(customer_id):
    customers = load_customers()
    
    for customer in customers:
        if customer.get('customer_id') == customer_id:
            return jsonify(customer), 200
    
    return jsonify({"error": "Customer not found"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
