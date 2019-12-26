﻿import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler

from handlers import * 
import settings



logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
			level = logging.INFO,
			filename='my_bot.log')

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


if __name__ == '__main__':
	main()