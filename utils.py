from random import choice
import logging

from clarifai.rest import ClarifaiApp
from emoji import emojize
from telegram import ReplyKeyboardMarkup, KeyboardButton

from db import update_user_emo
import settings

def get_keyboard():
	
	contactButton = KeyboardButton('Присалать контакты', request_contact=True)
	coordinateButton= KeyboardButton('Присалать координаты', request_location=True)

	my_keyboard = ReplyKeyboardMarkup([
										['Прислать котика', 'Сменить аватарку'],
										['Заполнить анкету'],
										[contactButton, coordinateButton]
									  ], 
									  resize_keyboard=True)


	return my_keyboard



def get_user_emo(user_data):
	if 'emo' not in user_data:
		user_data['emo'] = choice(settings.USER_EMOJI)
		update_user_emo(user_data)		
		
	return emojize(user_data['emo'], use_aliases=True)

def logging_input(update, info = None):
	logging.info(f'get message from {update.message.from_user.username}, message={update.message.text}')
	if info:
		logging.info(info)


def is_cat(filename):

	CODE_OK = 10000
	file_has_cat = False

	app = ClarifaiApp(api_key=settings.CLARIFAY_APY_KEY)
	model = app.public_models.general_model
	response = model.predict_by_filename(filename, max_concepts=5)
	
	try:
		if response['status']['code'] == CODE_OK:
			for concept in response['outputs'][0]['data']['concepts']:
				if concept['name'] == 'cat':
					file_has_cat = True
					break
		return file_has_cat
	except (IndexError, KeyError):
		logging.info('Ошибка при разборе ответа от clarifai')
		return False
