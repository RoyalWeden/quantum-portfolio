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
    if check_user(email, password) == None:
        new_user = {
            'email': email,
            'password': pass_encrypt(password),
            'subscription': subscription,
            'date_created': datetime.datetime.now(datetime.timezone.utc)
        }
        return users.insert_one(new_user).inserted_id
    return None

def check_user(email, password):
    '''Check if the user with the specified email and password is in the database'''
    found_user = users.find_one({
        'email': email,
        'password': pass_encrypt(password)
    })
    if found_user != None:
        return found_user['_id']
    return None

def pass_encrypt(password):
    '''Encrypts inputted password'''
    fernet = Fernet(config['PASS_KEY'])
    return fernet.encrypt(password.encode())

def pass_decrypt(password):
    '''Decrypts inputted password'''
    fernet = Fernet(config['PASS_KEY'])
    return fernet.decrypt(password).decode()