import time
import json
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 

KAFKA_BROKER = os.environ.get('KAFKA_BROKER_URL', 'kafka:9092')
TOPIC_NAME = os.environ.get('KAFKA_TOPIC', 'my-topic')
GROUP_ID = os.environ.get('KAFKA_GROUP_ID', 'my-group')

def get_consumer():
    consumer = None
    retries = 5
    while retries > 0 and consumer is None:
        try:
            consumer = KafkaConsumer(
                TOPIC_NAME,
                bootstrap_servers=[KAFKA_BROKER],
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                group_id=GROUP_ID,
                value_deserializer=lambda v: json.loads(v.decode('utf-8'))
            )
            logger.info("Kafka Consumer connected successfully.")
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}. Retrying in 5 seconds...")
            retries -= 1
            time.sleep(5)
    return consumer

if __name__ == "__main__":  
    consumer = get_consumer()
    if not consumer:
        logger.error("Could not initialize Kafka Consumer. Exiting.")
        exit(1)
        
    logger.info(f"Subscribed to topic '{TOPIC_NAME}' with group_id '{GROUP_ID}'")
    try:
        for message in consumer:
            logger.info(
                f"Received message: {message.value} "
                f"(Topic: {message.topic}, Partition: {message.partition}, Offset: {message.offset})"
            )
    except KeyboardInterrupt:
        logger.info("Consumer shutting down...")
    finally:
        if consumer:
            consumer.close()
        logger.info("Consumer closed.")