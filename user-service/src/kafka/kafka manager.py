from kafka_consumer import KafkaConsumer
import logging

class KafkaManager:

    def __init__(self, brokers, topic, group_id):

        self.consumer = KafkaConsumer(brokers, topic, group_id)

    def read_and_process(self):

        while True:

            try:

                msg = self.consumer.read_message()

                logging.info(f"Message received: {msg}")

            except TimeoutError:

                logging.warning("Message polling timeout occured")

            except Exception as e:

                logging.error(f"Error while reading message: {str(e)}")

    def stop(self):

        self.consumer.close()