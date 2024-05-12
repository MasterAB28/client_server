from flask import Flask, render_template, request, redirect, url_for
from kafka import KafkaProducer
import requests
import json
import os

app = Flask(__name__)

# Kafka configuration
KAFKA_SERVERS = os.getenv("KAFKA_HOST")
KAFKA_TOPIC = 'item_purchases'

# Connect to Kafka
producer = KafkaProducer(bootstrap_servers=KAFKA_SERVERS, value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# API server URL
API_URL = f'http://{os.getenv("API_HOST")}'

# Route to render the buy item form
@app.route('/')
def index():
    return render_template('menu.html')

# Route to handle buy requests
@app.route('/buy_item', methods=['GET', 'POST'])
def buy_item():
    if request.method == 'GET':
      return render_template('buy_item.html')
  
    if request.method == 'POST':    
        user_id = request.form.get('userId')
        item_id = request.form.get('itemId')
        
        # Produce message to Kafka
        message = f"{user_id},{item_id}"
        producer.send(KAFKA_TOPIC, value=message)
        
        return redirect(url_for('purchased_items'))

# Route to retrieve all purchased items from API server and render them
@app.route('/purchased_items', methods=['GET'])
def purchased_items():
    response = requests.get(f"{API_URL}/purchased_items")
    purchased_items = response.json()
    return render_template('purchased_items.html', purchased_items=purchased_items)

if __name__ == '__main__':
    app.run(port=8000)
