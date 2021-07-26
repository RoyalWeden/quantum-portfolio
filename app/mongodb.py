from app import config
from pymongo import MongoClient
import datetime
from cryptography.fernet import Fernet
from bson.objectid import ObjectId

client = MongoClient(config['MONGODB_URI'])
db = client['quantport']
stocks = db['stocks']
users = db['users']

def add_user(email, password, subscription):
    '''Adds a new user to the database, given an email, password, and subscription type'''
    new_user = {
        'email': email,
        'password': pass_encrypt(password),
        'subscription': subscription,
        'date_created': datetime.datetime.now(datetime.timezone.utc),
        'billing_info': {
            'country': '',
            'state': '',
            'city': '',
            'address1': '',
            'address2': '',
            'zipcode': ''
        },
        'portfolio_settings': {
            'stocks': [],
            'auto_generate_rate': 'manual',
            'last_generated_date': '',
            'next_generate_date': ''
        },
        'portfolios': []
    }
    return str(users.insert_one(new_user).inserted_id)

def check_user(email, password=None):
    '''Check if the user with the specified email and password is in the database'''
    found_user = users.find_one({
        'email': email
    })

    if not found_user:
        return None

    if password:
        found_password = pass_decrypt(found_user['password'])
        if password == found_password:
            return str(found_user['_id'])
        else:
            return None
    else:
        return str(found_user['_id'])

def pass_encrypt(password):
    '''Encrypts inputted password'''
    fernet = Fernet(bytes(config['PASS_KEY'], encoding='utf8'))
    return fernet.encrypt(password.encode())

def pass_decrypt(password):
    '''Decrypts inputted password'''
    fernet = Fernet(bytes(config['PASS_KEY'], encoding='utf8'))
    return fernet.decrypt(password).decode()

def set_billing_info(id, new_info):
    q = {'_id': ObjectId(id)}
    found_user = get_user_by_id(id)
    found_user['billing_info'] = new_info
    users.update_one(q, {'$set': found_user})

def get_billing_info(id):
    found_user = get_user_by_id(id)
    return found_user['billing_info']

def get_portfolio_settings(id):
    found_user = get_user_by_id(id)
    return found_user['portfolio_settings']

def set_portfolio_settings(id, new_settings):
    q = {'_id': ObjectId(id)}
    found_user = get_user_by_id(id)
    found_user['portfolio_settings'] = new_settings
    users.update_one(q, {'$set': found_user})

def set_account(id, new_account):
    q = {'_id': ObjectId(id)}
    found_user = get_user_by_id(id)
    found_user['email'] = new_account['email']
    found_user['password'] = pass_encrypt(new_account['password'])
    users.update_one(q, {'$set': found_user})

def get_email(id):
    return get_user_by_id(id)['email']

def get_user_by_id(id):
    return users.find_one({'_id': ObjectId(id)})

def delete_user_by_id(id):
    users.delete_one({'_id': ObjectId(id)})