from app import config
from pymongo import MongoClient
import datetime
from cryptography.fernet import Fernet

client = MongoClient(config['MONGODB_URI'])
db = client.database
stocks = db.stock_collection
users = db.users_collection

def add_user(email, password, subscription):
    '''Adds a new user to the database, given an email, password, and subscription type'''
    new_user = {
        'email': email,
        'password': pass_encrypt(password),
        'subscription': subscription,
        'date_created': datetime.datetime.now(datetime.timezone.utc)
    }
    return users.insert_one(new_user).inserted_id

def check_user(email, password=None):
    '''Check if the user with the specified email and password is in the database'''
    if password:
        found_user = users.find_one({
            'email': email,
            'password': pass_encrypt(password)
        })
    else:
        found_user = users.find_one({
            'email': email
        })
    if found_user != None:
        return found_user['_id']
    return None

def pass_encrypt(password):
    '''Encrypts inputted password'''
    fernet = Fernet(bytes(config['PASS_KEY'], encoding='utf8'))
    return fernet.encrypt(password.encode())

def pass_decrypt(password):
    '''Decrypts inputted password'''
    fernet = Fernet(bytes(config['PASS_KEY'], encoding='utf8'))
    return fernet.decrypt(password).decode()