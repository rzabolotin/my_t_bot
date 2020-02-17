from pymongo import MongoClient

import settings

db = MongoClient(settings.MONGO_PATH)[settings.MONGO_DBNAME]

def get_or_create_user(user_data):
    
    user = db.users.find_one({'user_id':user_data.id})
    if not user:
        user = {
                'user_id':user_data.id,
                'first_name':user_data.first_name,
                'last_name':user_data.last_name,
                'username':user_data.username,
            }
        db.users.insert_one(user)
    return user

def update_user_emo(user_data):
    db.users.update(
			{'user_id':user_data['user_id']},
			{'$set': {
				'emo':user_data['emo']
				}
			}
		)

def toggle_user_subscribe(user_data):
    old_value_subscibed = user_data.get('subscribed', False)
    user_data['subscribed'] = not old_value_subscibed
    db.users.update(
        {'user_id':user_data['user_id']},
        {'$set': {
            'subscribed':user_data['subscribed']}
        }
    )



def get_subscribed_users():
    return db.users.find({'subscribed':True})