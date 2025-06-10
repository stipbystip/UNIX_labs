import time
import json
import signal
from kafka import KafkaProducer
from kafka.errors import KafkaError
import os
import socket
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

KAFKA_BROKER = os.environ.get('KAFKA_BROKER_URL', 'kafka:9092')
TOPIC_NAME = os.environ.get('KAFKA_TOPIC', 'my-topic')

PRODUCER_ID = f"{os.environ.get('HOSTNAME', 'producer-unknown')}-{socket.gethostname()}"
logger.info(f"Starting producer with ID: {PRODUCER_ID}")

shutdown = False


def signal_handler(sig, frame):
    global shutdown
    logger.info(f"Received signal {sig}, shutting down gracefully...")
    shutdown = True


def get_producer():
    producer = None
    retries = 5
    while retries > 0 and producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=5
            )
            logger.info("Kafka Producer connected successfully.")
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}. Retrying in 5 seconds...")
            retries -= 1
            time.sleep(5)
    return producer


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    producer = get_producer()
    if not producer:
        logger.error("Could not initialize Kafka Producer after several retries. Exiting.")
        exit(1)

    count = 0
    try:
        while not shutdown:
            message = {
                'id': count,
                'producer': PRODUCER_ID,
                'message': f'Message {count} from {PRODUCER_ID}'
            }

            try:
                future = producer.send(TOPIC_NAME, value=message)
                record_metadata = future.get(timeout=10)

                logger.info(
                    f"Sent message: id={message['id']} to topic='{record_metadata.topic}' partition={record_metadata.partition} offset={record_metadata.offset}"
                )

            except KafkaTimeoutError:
                logger.warning("Failed to send message: Timeout. Flushing producer and retrying...")
                producer.flush()
            except KafkaError as e:
                logger.error(f"Error sending message: {e}")

            count += 1
            time.sleep(2)

    except Exception as e:
        logger.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)
    finally:
        if producer:
            logger.info("Flushing any pending messages...")
            producer.flush(timeout=10)
            logger.info("Closing producer...")
            producer.close()
        logger.info("Producer has been shut down.")
