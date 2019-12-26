from random import choice

from utils import get_keyboard, get_user_emo, logging_input

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
