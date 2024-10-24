from confluent_kafka import Consumer, KafkaError
import logging

class KafkaConsumer:

    def __init__(self, brokers, topic, group_id):
        
        self.topic = topic

        self.consumer = Consumer({
            'bootstrap.servers': brokers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })

        self.consumer.subscribe([self.topic])

    def read_message(self, timeout=5):

        try:

            msg = self.consumer.poll(timeout)

            if msg is None:

                raise Exception("No message received with the timeout period")
            
            if msg.error():
                
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    
                    logging.debug(f"Reached end of partition {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

                elif msg.error():

                    raise KafkaError(msg.error())
            
            return msg.value()
        
        except KafkaError as e:

            logging.error(f"Kafka error occured: {e}")
            
            raise e
        
        except Exception as e:

            logging.error(f"Error occured: {e}")
            
            raise e
    
    def close(self):
        self.consumer.close()
