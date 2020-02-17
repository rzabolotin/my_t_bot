from datetime import datetime
from glob import glob
import locale
import os
from random import choice

import dateutil.parser as parser
import ephem
from telegram import error, ReplyKeyboardRemove, ReplyKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler

from calculator import calculate
from db import get_or_create_user, toggle_user_subscribe, get_subscribed_users
import game_cities
from utils import get_keyboard, get_user_emo, logging_input, is_cat


def greet_user(update, context):
	
	logging_input(update)
	
	user = get_or_create_user(update.effective_user)

	text = f'Привет {get_user_emo(user)}'
	update.message.reply_text(text, reply_markup=get_keyboard())

def talk_to_me(update, context):
	
	logging_input(update)

	user = get_or_create_user(update.effective_user)

	if 'cities_game' in context.user_data:
		game_cities.cities_user_turn(update, context)
	else:

		message = 'Привет {} {}! Ты написал: {}'.format(update.message.from_user.username, 
														get_user_emo(user), 
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
	
	user = get_or_create_user(update.effective_user)

	if 'emo' in user:
		del user['emo']
	text = f'Вот твой новый аватар {get_user_emo(user)}'
	update.message.reply_text(text)
	
def get_contact(update, context):
	user = get_or_create_user(update.effective_user)
	print(update.message.contact)	
	text = f'Готово {get_user_emo(user)}'
	update.message.reply_text(text, reply_markup=get_keyboard())

def get_location(update, context):

	user = get_or_create_user(update.effective_user)

	print(update.message.location)	
	text = f'Готово {get_user_emo(user)}'
	update.message.reply_text(text, reply_markup=get_keyboard())

def start_cities_game(update, context):
	
	logging_input(update)
	user = get_or_create_user(update.effective_user)


	context.user_data['cities_game'] = game_cities.get_cities_for_game()
	context.user_data['cities_start_letter'] = ''
	
	logging.info("Начинаем играть в города")

	update.message.reply_text(f'Начинаем играть в города {get_user_emo(user)}')

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

def anketa_start(update, context):
	update.message.reply_text('Как вас зовут? Напишите имя и фамилию.', reply_markup=ReplyKeyboardRemove())
	return 'anketa_name'

def anketa_name(update, context):
	
	answer = update.message.text
	if len(answer.split()) != 2:
		update.message.reply_text('Укажите Имя и Фамилию (2 слова)')
		return 'anketa_name'
	
	context.user_data['anketa_name'] = answer

	my_keyboard = ReplyKeyboardMarkup([['1','2','3','4','5']], one_time_keyboard=True)

	update.message.reply_text('Оцените качество работы сервиса', reply_markup=my_keyboard)
	return 'anketa_rating'

def anketa_rating(update, context):
	
	context.user_data['anketa_rating'] = update.message.text

	update.message.reply_text("""Напишите краткий отзыв о работе сервиса
или /skip для пропуска шага""")
	return 'anketa_comment'

def anketa_comment(update, context):
	context.user_data['anketa_comment'] = update.message.text

	anketa_text = """
<b>Имя</b>: {anketa_name}
<b>Оценка</b>: {anketa_rating}
<b>Комментарий</b>: {anketa_comment}
	""".format(**context.user_data)
	update.message.reply_text(anketa_text, parse_mode = ParseMode.HTML, reply_markup=get_keyboard())
	return ConversationHandler.END

def anketa_skip_comment(update, context):

	anketa_text = """
<b>Имя</b>: {anketa_name}
<b>Оценка</b>: {anketa_rating}
	""".format(**context.user_data)
	update.message.reply_text(anketa_text, parse_mode = ParseMode.HTML, reply_markup=get_keyboard())
	return ConversationHandler.END

def anketa_dont_understand(update, context):
	update.message.reply_text('Не понял Вас')

def send_spam(context):
	spam_message = 'Lovely Spam! Wonderful Spam!!'
	for user in get_subscribed_users():
		try:
			context.bot.sendMessage(chat_id=user['user_id'], text = spam_message)
		except (error.BadRequest):
			print('Can\'t find chat {}'.format(user['user_id']))


def spam_subscribe(update, context):
	
	logging_input(update)
	user = get_or_create_user(update.effective_user)

	if user.get('subscribed', False):
		message = get_user_emo(user) + ', ты уже подписан'
	else:
		toggle_user_subscribe(user)
		message = f'{get_user_emo(user)}, ты подписался на спам ;)'

	update.message.reply_text(message, reply_markup=get_keyboard())

def spam_unsubscribe(update, context):
	
	logging_input(update)
	user = get_or_create_user(update.effective_user)

	
	if not user.get('subscribed', False):
		message = get_user_emo(user) + ', ты и так не подписан'
	else:
		toggle_user_subscribe(user)
		message = f'{get_user_emo(user)}, мы тебя убрали из списка'
	
	update.message.reply_text(message, reply_markup=get_keyboard())

def set_alarm(update, context):

	logging_input(update)

	alarm_args = update.message.text.split()
	try:
		interval = int(alarm_args[1])
	except (ValueError, IndexError):
		update.message.reply_text('Не понятно, когда запустить будильник', reply_markup=get_keyboard())
		return
	
	context.job_queue.run_once(alarm, interval, context=update.message.chat_id)

	update.message.reply_text('Будильник установлен!KP', reply_markup=get_keyboard())

def alarm(context):
	context.bot.sendMessage(chat_id=context.job.context, text = '!!!!Вам напоминание!!!!')