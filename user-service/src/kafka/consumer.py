from confluent_kafka import Consumer as KafkaBaseConsumer
from fastapi import Depends
import json
from src.config.base_config import get_base_config, BaseConfig
from .events import USER_EVENTS
from src.svc.user.service import get_user_service, UserService

class KafkaConsumer:

    def __init__(self, baseConfig: BaseConfig, topic: str, group_id: str):
        config = baseConfig.USER_PRODUCER

        self.consumer_config = {
            "bootstrap.servers": config.bootstrap_servers,
            "security.protocol": config.security_protocol,
            "client.id": config.client_id, 
        }

        self.consumer = KafkaBaseConsumer(self.consumer_config)
        self.topic = topic

    def consume(self):
        self.consumer.subscribe([self.topic])

        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    raise Exception(f"Consumer error: {msg.error()}")

                try:
                    kafka_message = json.loads(msg.value().decode('utf-8'))
                    self.handle_kafka_message(kafka_message)
                except Exception as e:
                    raise Exception(f"Failed to handle kafka message: {str(e)}")

        finally:
            self.consumer.close()

    def handle_kafka_message(self, kafka_message):
        raise NotImplementedError("Subclasses must implement this method")


class InsertUserConsumer(KafkaConsumer):
    def __init__(self, baseConfig: BaseConfig):
        super().__init__(baseConfig, topic="user-topic", group_id="user-insert-consumer")

    def handle_kafka_message(self, kafka_message: dict):
        if kafka_message.get("event") == USER_EVENTS.CREATED:
            user_data = kafka_message.get("payload")
            user_service: UserService = get_user_service()
            user_service.register_user(user_data.get("email"))
            print(f"Inserted user: {user_data.get('email')}")


class UpdateUserConsumer(KafkaConsumer):
    def __init__(self, baseConfig: BaseConfig):
        super().__init__(baseConfig, topic="user-topic", group_id="user-update-consumer")

    def handle_kafka_message(self, kafka_message: dict):
        if kafka_message.get("event") == USER_EVENTS.UPDATED:
            user_data = kafka_message.get("payload")
            print(f"Updating user: {user_data.get('email')}")



class DeleteUserConsumer(KafkaConsumer):
    def __init__(self, baseConfig: BaseConfig):
        super().__init__(baseConfig, topic="user-topic", group_id="user-delete-consumer")

    def handle_kafka_message(self, kafka_message: dict):
        if kafka_message.get("event") == USER_EVENTS.DELETED:
            user_data = kafka_message.get("payload")
            print(f"Deleting user with ID: {user_data.get('id')}")



async def get_insert_user_consumer(config: BaseConfig = Depends(get_base_config)) -> InsertUserConsumer:
    return InsertUserConsumer(config)

async def get_update_user_consumer(config: BaseConfig = Depends(get_base_config)) -> UpdateUserConsumer:
    return UpdateUserConsumer(config)

async def get_delete_user_consumer(config: BaseConfig = Depends(get_base_config)) -> DeleteUserConsumer:
    return DeleteUserConsumer(config)

# from confluent_kafka import Consumer
# from fastapi import Depends
# from src.config.base_config import get_base_config, BaseConfig
# import json
# from .events import USER_EVENTS
# from src.svc.user.service import get_user_service, UserService

# class KafkaConsumer:

#     def __init__(self, baseConfig:BaseConfig, topic:str):
        
#         config = baseConfig.USER_CONSUMER

#         self.consumer_config = {
#             "bootstrap.servers": config.bootstrap_servers,
#             "security.protocol": config.security_protocol,
#             "sasl.mechanisms": config.sasl_mechanism,
#             "sasl.username": config.sasl_username,
#             "group.id": "",
#             "sasl.password": config.sasl_password,
#         }

#         self.consumer = Consumer(self.consumer_config)

#         self.topic = topic

#     def consume(self):

#         self.consumer.subscribe([self.topic])

#         try:

#             while True:

#                 msg = self.consumer.poll(timeout=1.0)

#                 if msg is None:

#                     continue

#                 if msg.error():

#                     raise Exception(f"Consumer error: {msg.error()}")
                
#                 try:

#                     kafka_message = json.loads(msg.value().decode('utf-8'))

#                     self.handle_kafka_message(kafka_message)

#                 except Exception as e:

#                     raise Exception(f"Failed to handle kafka message: {str(e)}")
                
#         finally:
#             self.consumer.close()

#     def handle_kafka_message(self, kafka_message):
#         """Subclasses must implement this method to handle messages."""
#         raise NotImplementedError("Subclasses should implement this method")


# class InsertUserConsumer(Consumer):

#     def __init__(self, baseConfig):

#         super().__init__(baseConfig)

#         self.consumer_config['group.id'] = "user-insert-consumer"

#         self.consumer = KafkaConsumer(self.consumer_config, "user-topic")

#     def handle_kafka_message(self, kafka_message:dict):

#         if kafka_message.get("event") == USER_EVENTS.CREATED:

#             user_data = kafka_message.get("payload")

#             user_service: UserService = get_user_service()

#             user_service.register_user(user_data.get("email"))



# class UpdateUserConsumer(Consumer):

#     def __init__(self, baseConfig):

#         super().__init__(baseConfig)

#         self.consumer_config['group.id'] = "user-update-consumer"

# class DeleteUserConsumer(Consumer):

#     def __init__(self, baseConfig):

#         super().__init__(baseConfig)

#         self.consumer_config['group.id'] = "user-delete-consumer"




# async def get_consumer(config:BaseConfig = Depends(get_base_config)) -> Consumer:

#     return KafkaConsumer(config)

# async def get_insert_user_consumer(config:BaseConfig = Depends(get_base_config)) -> InsertUserConsumer:

#     return InsertUserConsumer(config, "user-topic")

# async def get_update_user_consumer(config:BaseConfig = Depends(get_base_config)) -> UpdateUserConsumer:

#     return UpdateUserConsumer(config, "user-topic")

# async def get_delete_user_consumer(config:BaseConfig = Depends(get_base_config)) -> DeleteUserConsumer:

#     return DeleteUserConsumer(config, "user-topic")