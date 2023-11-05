import os

from motor.motor_asyncio import AsyncIOMotorClient

mongo_password_file = os.environ["MONGO_PASSWORD_FILE"]
with open(mongo_password_file, 'r') as file:
    mongo_password = file.read()

ENV = os.environ["ENV"]
if ENV == 'LOCAL':
    host = 'localhost'
elif ENV == 'DOCKER':
    host = 'mongo_database'
else:
    raise Exception('Invalid environment config!')

user = 'root'

mongo_client = AsyncIOMotorClient(f"mongodb://{user}:{mongo_password}@{host}")
database = mongo_client["medicinal_object_database"]
