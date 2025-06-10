import time
import json
import signal
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import os
import socket
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BROKER = os.environ.get('KAFKA_BROKER_URL', 'kafka:9092')
TOPIC_NAME = os.environ.get('KAFKA_TOPIC', 'my-topic')
GROUP_ID = os.environ.get('KAFKA_GROUP_ID', 'my-group')

CONSUMER_ID = f"{os.environ.get('HOSTNAME', 'consumer-unknown')}-{socket.gethostname()}"
logger.info(f"Starting consumer with ID: {CONSUMER_ID}")

shutdown = False


def signal_handler(sig, frame):
    global shutdown
    logger.info(f"Received signal {sig}, shutting down gracefully...")
    shutdown = True


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

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    consumer = get_consumer()
    if not consumer:
        logger.error("Could not initialize Kafka Consumer. Exiting.")
        exit(1)

    logger.info(f"Subscribed to topic '{TOPIC_NAME}' with group_id '{GROUP_ID}'")
    try:
        while not shutdown:
            records = consumer.poll(timeout_ms=1000, max_records=10)
            if not records:
                continue

            for topic_partition, messages in records.items():
                for message in messages:
                    value = message.value
                    logger.info(
                        f"[{CONSUMER_ID}] Received: {value} "
                        f"(Partition: {message.partition}, Offset: {message.offset})"
                    )


    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        if consumer:
            logger.info("Closing consumer and committing offsets...")
            try:

                consumer.commit()
                consumer.close()
            except KafkaError as e:
                logger.error(f"Error during shutdown: {e}")
        logger.info("Consumer closed.")
