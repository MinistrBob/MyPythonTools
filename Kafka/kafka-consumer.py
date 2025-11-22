from kafka import KafkaConsumer
import traceback

def consume_messages(broker_address, topic_name, sasl_username=None, sasl_password=None):
    consumer = None
    try:
        # Create KafkaConsumer with SASL/PLAIN authentication
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=[broker_address],
            security_protocol="SASL_PLAINTEXT",
            sasl_mechanism="PLAIN",
            sasl_plain_username=sasl_username,
            sasl_plain_password=sasl_password,
            auto_offset_reset='earliest',  # Start reading at the earliest message
            enable_auto_commit=True,
            # group_id='my-group'
        )

        # Consume messages
        for message in consumer:
            print(f"Received message: {message.value.decode('utf-8')}")

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

    finally:
        # Ensure the consumer is closed
        try:
            if consumer is not None:
                consumer.close()
        except Exception as e:
            print(f"Error closing Kafka consumer: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    # broker_address = "kafka-dev-0.kafka-headless-dev.gasps.svc.cluster.local:9092"
    broker_address = "172.26.12.190:31301"
    topic_name = "connection-test"
    # Use your SASL credentials here
    sasl_username = "admin"
    sasl_password = "admin"
    consume_messages(broker_address, topic_name, sasl_username, sasl_password)
