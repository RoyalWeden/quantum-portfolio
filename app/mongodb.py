from app import config
from pymongo import MongoClient
import datetime
from cryptography.fernet import Fernet
from bson.objectid import ObjectId
import uuid
import random

client = MongoClient(config['MONGODB_URI'])
db = client['quantport']
users = db['users']

def add_user(email, password, subscription):
    '''Adds a new user to the database, given an email, password, and subscription type'''
    new_user = {
        'email': email,
        'password': pass_encrypt(password),
        'subscription': subscription,
        'verification': {
            'status': 'pending',
            'time_left': 600,
            'uuid': str(uuid.uuid4()),
            'code': pass_encrypt(str(random.randrange(1000000, 9999999))),
        },
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
            'optimize_count': 0,
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

def add_optimized_portfolio(id, opt_portfolio=None, pending_portfolio=None):
    q = {'_id': ObjectId(id)}
    found_user = get_user_by_id(id)
    if opt_portfolio:
        found_user['portfolios'].pop(0)
        found_user['portfolios'].insert(0, opt_portfolio)
    elif pending_portfolio:
        found_user['portfolios'].insert(0, pending_portfolio)
    users.update_one(q, {'$set': found_user})

def elapse_portfolio_time(id, updated_portfolio):
    q = {'_id': ObjectId(id)}
    found_user = get_user_by_id(id)
    found_user['portfolios'][0] = updated_portfolio
    users.update_one(q, {'$set': found_user})

def get_portfolios(id):
    found_user = get_user_by_id(id)
    if not found_user:
        return None
    return found_user['portfolios']

def get_email(id):
    return get_user_by_id(id)['email']

def get_user_by_id(id):
    return users.find_one({'_id': ObjectId(id)})

def delete_user_by_id(id):
    users.delete_one({'_id': ObjectId(id)})

def check_verify_code(url_id, url_uuid, code):
    found_user = get_user_by_id(url_id)
    is_verified = False
    if found_user:
        is_verified = code == pass_decrypt(found_user['verification']['code']) and url_uuid == found_user['verification']['uuid'] and found_user['verification']['time_left'] > 0
        if is_verified:
            found_user['verification']['status'] = 'verified'
            q = {'_id': ObjectId(url_id)}
            users.update_one(q, {'$set': found_user})
    return is_verified

def is_verified_user(id):
    found_user = get_user_by_id(id)
    if found_user != None:
        return found_user['verification']['status'] == 'verified'
    return False