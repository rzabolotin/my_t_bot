from random import choice
import logging

from emoji import emojize
from telegram import ReplyKeyboardMarkup, KeyboardButton

import settings

def get_keyboard():
	
	contactButton = KeyboardButton('Присалать контакты', request_contact=True)
	coordinateButton= KeyboardButton('Присалать координаты', request_location=True)

	my_keyboard = ReplyKeyboardMarkup([
										['Прислать котика', 'Сменить аватарку'],
										[contactButton, coordinateButton]
									  ], 
									  resize_keyboard=True)


	return my_keyboard



def get_user_emo(user_data):
	if 'emo' in user_data:
		return user_data['emo']
	else:
		user_data['emo'] = emojize(choice(settings.USER_EMOJI), use_aliases=True)
		return user_data['emo']


def logging_input(update):
	logging.info(f'get message from {update.message.from_user.username}, message={update.message.text}')