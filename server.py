from flask import Flask, request, jsonify
from kafka import KafkaProducer
import os
import json
import time

app = Flask(__name__)

def get_producer():
    while True:
        try:
            return KafkaProducer(bootstrap_servers=os.environ['KAFKA_BOOTSTRAP_SERVERS'])
        except Exception as e:
            print("Waiting for Kafka to be available:", e)
            time.sleep(5)

producer = get_producer()

@app.route('/sensor_data', methods=['POST'])
def receive_data():
    data = request.get_json()
    producer.send('sensor_data_topic', json.dumps(data).encode('utf-8'))
    return jsonify({'message': 'Data sent to Kafka successfully'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

