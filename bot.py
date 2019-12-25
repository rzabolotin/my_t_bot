from datetime import datetime
from glob import glob
import logging
from random import choice


from emoji import emojize
import ephem
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler

from calculator import calculate
import settings


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
			level = logging.INFO,
			filename='bot.log')

def greet_user(update, context):
	
	text = f'Привет {get_user_emo(context.user_data)}'
	
	update.message.reply_text(text, reply_markup=get_keyboard())

	#logging.info(text)

def talk_to_me(update, context):
	
	if 'cities_game' in context.user_data:
		cities_user_turn(update, context)
	else:

		message = 'Привет {} {}! Ты написал: {}'.format(update.message.from_user.username, 
														get_user_emo(context.user_data), 
														update.message.text)
		logging.info(message)
		update.message.reply_text(message, reply_markup=get_keyboard())
	
def get_user_emo(user_data):
	if 'emo' in user_data:
		return user_data['emo']
	else:
		user_data['emo'] = emojize(choice(settings.USER_EMOJI), use_aliases=True)
		return user_data['emo']
	
def print_planet_constellation(update, context):


	input_text = update.message.text
	logging.info(f'get command planet {input_text}')
	
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

	import ephem
	from datetime import datetime
	import dateutil.parser as parser
	import locale

	locale.setlocale(locale.LC_ALL, 'rus_rus')

	input_text = update.message.text
	logging.info(f'get command planet {input_text}')
	
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
	if 'emo' in context.user_data:
		del context.user_data['emo']
	text = f'Вот твой новый аватар {get_user_emo(context.user_data)}'
	update.message.reply_text(text)
	#logging.info(text)

def get_keyboard():
	
	contactButton = KeyboardButton('Присалать контакты', request_contact=True)
	coordinateButton= KeyboardButton('Присалать координаты', request_location=True)

	my_keyboard = ReplyKeyboardMarkup([
										['Прислать котика', 'Сменить аватарку'],
										[contactButton, coordinateButton]
									  ], 
									  resize_keyboard=True)


	return my_keyboard

def get_contact(update, context):
	print(update.message.contact)	
	text = f'Готово {get_user_emo(context.user_data)}'
	update.message.reply_text(text, reply_markup=get_keyboard())

def get_location(update, context):
	print(update.message.location)	
	text = f'Готово {get_user_emo(context.user_data)}'
	update.message.reply_text(text, reply_markup=get_keyboard())

def get_cities_for_game():
	return [
		'москва',
		'астрахань',
		'новосибирск',
		'киев',
		'воркута',
		'анадырь',
		'рига',
		'архангельск',
		'канберра',
		'атланта',
		'анталия'
	]

def cities_bot_turn(update, context):
	my_city = get_next_city(context.user_data['cities_start_letter'], context.user_data['cities_game'])
	if not my_city:
		text = 'У меня нет больше варианта, сдаюсь'
		del context.user_data['cities_game']
	else:
		text = f'{my_city.capitalize()}, ваш ход'
		start_letter = my_city[-1]
		if start_letter == 'ь':
			start_letter = my_city[-2]
		context.user_data['cities_start_letter'] = start_letter
	update.message.reply_text(text, reply_markup=get_keyboard())

	if (my_city
	   and not get_variants(context.user_data['cities_start_letter'], context.user_data['cities_game'])):
		text = 'Больше нет вариантов. Игра закончилась. Я выиграл'
		del context.user_data['cities_game']
		update.message.reply_text(text, reply_markup=get_keyboard())

def cities_user_turn(update, context):
	user_city = update.message.text.lower()
	result, text = check_user_city(user_city,
								   context.user_data['cities_start_letter'],
								   context.user_data['cities_game'])
	update.message.reply_text(text, reply_markup=get_keyboard())
	
	if result:
		start_letter = user_city[-1]
		if start_letter == 'ь':
			start_letter = user_city[-2]
		context.user_data['cities_start_letter'] = start_letter
		cities_bot_turn(update, context)
	
def check_user_city(user_city:str, start_letter:str, cities_game:list) -> [str, bool]:
	if user_city not in cities_game:
		return False, 'Я не знаю такого города'
	elif user_city[0] != start_letter:
		return False, f'Твой город начинается на {user_city[0].upper()}, а нужно на {start_letter.upper()}'
	elif not user_city:
		return True, 'В списке закончились города'
	else:
		cities_game.remove(user_city)
		return True, 'Отлично'

def get_next_city(start_letter:str, cities_game:list) -> [str, bool]:
	if start_letter == "":
		matches = cities_game
	else:
		matches = [x for x in cities_game if x[0] == start_letter]

	if not matches:
		return False

	my_city = choice(matches)
	cities_game.remove(my_city)

	return my_city

def get_variants(start_letter:str, cities_game:list) -> [str, bool]:
	if start_letter == "":
		matches = cities_game
	else:
		matches = [x for x in cities_game if x[0] == start_letter]

	return matches

def start_cities_game(update, context):
	
	context.user_data['cities_game'] = get_cities_for_game()
	context.user_data['cities_start_letter'] = ''
	
	logging.info("Начинаем играть в города")

	update.message.reply_text(f'Начинаем играть в города {get_user_emo(context.user_data)}')

	cities_bot_turn(update, context)


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


def main():
	mybot = Updater(settings.TOKEN, request_kwargs=settings.PROXY, use_context=True)
		
	dp = mybot.dispatcher
	dp.add_handler(CommandHandler('start', greet_user))
	dp.add_handler(CommandHandler('planet', print_planet_constellation))
	dp.add_handler(CommandHandler('word_count', word_count))
	dp.add_handler(CommandHandler('next_full_moon', next_full_moon))
	dp.add_handler(CommandHandler('cats', give_kitty))
	dp.add_handler(CommandHandler('calc', lets_calculate))
	dp.add_handler(CommandHandler('cities', start_cities_game))
	dp.add_handler(MessageHandler(Filters.regex('^(Прислать котика)$'), give_kitty))
	dp.add_handler(MessageHandler(Filters.regex('^(Сменить аватарку)$'), change_avatar))
	dp.add_handler(MessageHandler(Filters.contact, get_contact))
	dp.add_handler(MessageHandler(Filters.location, get_location))
	dp.add_handler(MessageHandler(Filters.text, talk_to_me))

	logging.info('starting bot')


	mybot.start_polling()
	mybot.idle()


main()