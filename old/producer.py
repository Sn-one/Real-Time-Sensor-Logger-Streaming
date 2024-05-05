from confluent_kafka import Producer
import sys
import json

KAFKA_TOPIC = 'your_topic'
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'


# Kafka producer
def kafka_producer(sensor_data):
    p = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})

    def delivery_report(err, msg):
        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

    # Convert sensor_data to string as Kafka messages must be strings, bytes, or None
    sensor_data_str = json.dumps(sensor_data)

    p.produce(KAFKA_TOPIC, sensor_data_str, callback=delivery_report)

    p.flush()
