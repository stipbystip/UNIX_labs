import time
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)  

KAFKA_BROKER = os.environ.get('KAFKA_BROKER_URL', 'kafka:9092')
TOPIC_NAME = os.environ.get('KAFKA_TOPIC', 'my-topic')

def get_producer():
    producer = None
    retries = 5
    while retries > 0 and producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3
            )
            logger.info("Kafka Producer connected successfully.")
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}. Retrying in 5 seconds...")
            retries -= 1
            time.sleep(5)
    return producer

if __name__ == "__main__":  
    producer = get_producer()
    if not producer:
        logger.error("Could not initialize Kafka Producer. Exiting.")
        exit(1)

    count = 0
    try:
        while True:
            message = {
                'id': count,
                'message': f'Hello Kafka! Message number {count}'
            }
            future = producer.send(TOPIC_NAME, value=message)
            
            try:
                record_metadata = future.get(timeout=10)
                logger.info(f"Sent message: {message} to topic '{record_metadata.topic}' partition {record_metadata.partition} offset {record_metadata.offset}")
            except KafkaError as e:
                logger.error(f"Error sending message: {e}")

            producer.flush()
            count += 1
            time.sleep(2)
    except KeyboardInterrupt:
        logger.info("Producer shutting down...")
    finally:
        if producer:
            producer.close()
        logger.info("Producer closed.")