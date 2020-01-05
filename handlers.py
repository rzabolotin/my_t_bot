from datetime import datetime
from glob import glob
import locale
import os
from random import choice

import dateutil.parser as parser
import ephem

import game_cities
from calculator import calculate
from utils import get_keyboard, get_user_emo, logging_input, is_cat


def greet_user(update, context):
	
	logging_input(update)
	
	text = f'Привет {get_user_emo(context.user_data)}'
	update.message.reply_text(text, reply_markup=get_keyboard())

def talk_to_me(update, context):
	
	logging_input(update)
	
	if 'cities_game' in context.user_data:
		game_cities.cities_user_turn(update, context)
	else:

		message = 'Привет {} {}! Ты написал: {}'.format(update.message.from_user.username, 
														get_user_emo(context.user_data), 
														update.message.text)
		update.message.reply_text(message, reply_markup=get_keyboard())
	
def print_planet_constellation(update, context):

	logging_input(update)
	
	input_text = update.message.text
	
	parameters = input_text.split()

	if len(parameters)<2:
		answer = 'не передан параметр для команды'

	planet_name = parameters[1]

	our_plantes = {
					'MARS':ephem.Mars,
					'VENUS':ephem.Venus,
					'MOON':ephem.Moon,
					'SUN':ephem.Sun,
					'MERCURY':ephem.Mercury
					}

	
	if planet_name.upper() in our_plantes:
		planet = our_plantes[planet_name.upper()](datetime.now())
		cons = ephem.constellation(planet)
		answer = f'{planet_name.upper()} в создвездии {cons[1]}'
	else:
		answer = f'не найдена планета {planet_name}'
	
	update.message.reply_text(answer, reply_markup=get_keyboard())

def next_full_moon(update, context):

	logging_input(update)

	locale.setlocale(locale.LC_ALL, 'rus_rus')

	input_text = update.message.text
	
	parameters = input_text.split()

	if (len(parameters) == 1
		or parameters[1] == 'today'
		or parameters[1] == 'сегодня'):
		date = datetime.now()
	else:
		datestirng = ' '.join(parameters[1:])
		date = parser.parse(datestirng)

	answer = ephem.next_full_moon(date).datetime().strftime('%A %d %B %Y')
	
	update.message.reply_text(answer, reply_markup=get_keyboard())

def word_count(update, context):

	parameters = update.message.text.split()[1:]


	parameters = [x for x in parameters if not x.isdigit()]
	
	if len(parameters) == 0:
		answer = 'у вас пустое предложение'
	else:
		answer = f'ваше предолжение содержит {len(parameters)} слов'

	update.message.reply_text(answer, reply_markup=get_keyboard())

def give_kitty(update, context):
	cat_list = glob('cats/cat*.jpg')
	cat_picture = choice(cat_list)
	context.bot.send_photo(chat_id = update.message.chat_id, photo=open(cat_picture, 'rb'))
	
def change_avatar(update, context):
	logging_input(update)
	if 'emo' in context.user_data:
		del context.user_data['emo']
	text = f'Вот твой новый аватар {get_user_emo(context.user_data)}'
	update.message.reply_text(text)
	
def get_contact(update, context):
	print(update.message.contact)	
	text = f'Готово {get_user_emo(context.user_data)}'
	update.message.reply_text(text, reply_markup=get_keyboard())

def get_location(update, context):
	print(update.message.location)	
	text = f'Готово {get_user_emo(context.user_data)}'
	update.message.reply_text(text, reply_markup=get_keyboard())

def start_cities_game(update, context):
	
	logging_input(update)

	context.user_data['cities_game'] = game_cities.get_cities_for_game()
	context.user_data['cities_start_letter'] = ''
	
	logging.info("Начинаем играть в города")

	update.message.reply_text(f'Начинаем играть в города {get_user_emo(context.user_data)}')

	game_cities.cities_bot_turn(update, context)

def lets_calculate(update, context):
	expr = update.message.text.split()
	expr = ''.join(expr[1:])
	try:
		res = calculate(expr)
	except ZeroDivisionError:
		res = 'не могу делить на ноль'
	except ValueError as e:
		res = f'не могу распозрать {e}'
	update.message.reply_text(f'результат = {res}')


def add_cat_photo(update, context):
	update.message.reply_text('Обрабатываю фото')
	logging_input(update, 'Получили фотографию, может быть котик')

	os.makedirs('downloads', exist_ok=True)
	photo_file = context.bot.getFile(update.message.photo[-1].file_id)
	filename = os.path.join('downloads', f'{photo_file.file_id}.jpg')
	photo_file.download(filename)
	update.message.reply_text('Файл сохранен')

	if is_cat(filename):
		new_filename = os.path.join('cats', f'cat_{photo_file.file_id}.jpg')
		os.rename(filename, new_filename)
		update.message.reply_text('Обнаружен котик. Забираем его к себе.')
		logging_input(update, f'Добавили котика в базу фоточек. {new_filename}')
	else:
		os.remove(filename)
		update.message.reply_text('Что вы прислали ?! Тут нет котиков!')


		


