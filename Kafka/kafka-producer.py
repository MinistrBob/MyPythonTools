from kafka import KafkaProducer
import traceback

def produce_messages(broker_address, topic_name, messages, sasl_username=None, sasl_password=None):
    try:
        # Create KafkaProducer with SASL/PLAIN authentication
        producer = KafkaProducer(
            bootstrap_servers=[broker_address],
            security_protocol="SASL_PLAINTEXT",
            sasl_mechanism="PLAIN",
            sasl_plain_username=sasl_username,
            sasl_plain_password=sasl_password,
            value_serializer=lambda v: str(v).encode('utf-8')
        )

        # Send each message to the specified topic
        for message in messages:
            producer.send(topic_name, value=message)
            print(f"Sent message: {message}")

        # Block until all messages are sent
        producer.flush()

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

    finally:
        # Ensure the producer is closed
        try:
            producer.close()
        except Exception as e:
            print(f"Error closing Kafka producer: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    broker_address = "kafka-dev-0.kafka-headless-dev.gasps.svc.cluster.local:9092"
    topic_name = "connection-test"
    messages = ["Message3", "Message444"]
    # Use your SASL credentials here
    sasl_username = "admin"
    sasl_password = "admin"
    produce_messages(broker_address, topic_name, messages, sasl_username, sasl_password)
