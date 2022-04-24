import json
from textwrap import wrap

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import (
	ReplyKeyboardMarkup, 
	KeyboardButton, 
	InlineKeyboardButton
)
from configparser import ConfigParser

from models import Model, UserModel


settings = ConfigParser()
settings.read('settings.ini')

db = settings['DB']

bot = Bot(token=settings['BOT']['token'])
dp = Dispatcher(bot)


class BotApp:
	async def start_menu(self, msg, bot):
		if msg.text == '/start':
			try:
				UserModel(path='DataBase.db').create_user(user_id=msg.from_user.id)
			except:
				pass

			start_menu = KeyboardButton(text='Выбрать продукты')
			cook = KeyboardButton(text='Показать возможные блюда')
			clear = KeyboardButton(text='Очистить')
			reply = ReplyKeyboardMarkup(resize_keyboard=True)
			reply.add(start_menu)
			reply.add(cook)
			reply.add(clear)

			await bot.send_message(chat_id=msg.from_user.id, text=f'''Здравствуйте {msg.from_user.first_name} я помогу вам приготовить блюдо, какие продукты у вас есть?''', reply_markup=reply)



class CookingReturn(BotApp):
	def __init__(self, user_id=None, bot=None):
		self.user_id = user_id
		self.bot = bot

	async def cook(self, bot, msg):
		if msg.text == 'Показать возможные блюда':
			show = UserModel(path='DataBase.db').show(user_id=msg.from_user.id)
			if len(show) == 0 and len(show) < 3:
				await bot.send_message(chat_id=msg.from_user.id, 
				text='Вы выбрали недостаточно продуктов. Выберите хотя бы 3 продукта')
			else:
				show_user = wrap(text=show, width=4)
				cookings = Model('DataBase.db').cooke()
				history_msg = list()
				x = 0
				
				while x <= len(show_user):
					for i in show_user:
						try:
							if i in cookings[x][4]:
								if cookings[x][1] in history_msg:
									pass
								else:
									message = f'{cookings[x][1]}\nСпособ приготовления:\n{cookings[x][5]}\nСложность приготовления:\n{cookings[x][3]}\nВремя приготовления:\n{cookings[x][2]}'
									await bot.send_message(chat_id=msg.from_user.id, text=message)
									history_msg.append(cookings[x][1])
						except IndexError:
							pass
					x+=1
					
		
	async def run(self, bot, msg, id:str=None):
		l = wrap(text=id, width=4)
		cooke_list = Model('DataBase.db').cooke()
		for cooke in cooke_list:
			if sorted(''.join(l)) == sorted(cooke[4]):
				message = f'{cooke[1]}\nСпособ приготовления:\n{cooke[5]}\nСложность приготовления:\n{cooke[3]}\nВремя приготовления:\n{cooke[2]}'
				await bot.send_message(chat_id=msg.from_user.id, text=message)
				UserModel(path='DataBase.db').update(user_id=msg.from_user.id, history="")



class ProductItems(BotApp):
	def __init__(self):
		self.json_obj = {"inline_keyboard": []}

	async def product_type(self, msg, bot):
		if msg.text == 'Выбрать продукты':
			button_add = InlineKeyboardButton('Продолжить ➡️', callback_data='next')
			# Формирование клавиатуры списка продуктов
			product_type_list = Model('DataBase.db')

			for name in product_type_list.product_type():
				self.json_obj['inline_keyboard'].append([{"text": name, "callback_data": name}])

			await bot.send_message(chat_id=msg.from_user.id, 
			text='Выберите продукты:', reply_markup=json.dumps(self.json_obj))
			# Очистка
			self.json_obj=[]

	async def product_list(self, msg, bot):
		if msg.data in Model('DataBase.db').product_type():
			product_list = Model('DataBase.db')

			for item in product_list.product(product_type=msg.data):
				self.json_obj['inline_keyboard'].append([{"text": item[1], "callback_data": item[0]}])
			
			await bot.send_message(chat_id=msg.from_user.id, 
			text=f'Продукты типа "{msg.data}" которые есть в наличии: ', 
			reply_markup=json.dumps(self.json_obj))
			# Очистка
			self.json_obj=[]

	async def add_product(self, msg, bot):
		lists = Model('DataBase.db').product(product_type="all")
		if msg.data in lists:
			# Формирование нового ID
			show_user_history = UserModel(path='DataBase.db').show(user_id=msg.from_user.id)
			cooking_ids = show_user_history + msg.data
			UserModel(path='DataBase.db').update(user_id=msg.from_user.id, history=cooking_ids)
			# Реакция бота
			user_product = Model('DataBase.db').product_name(ids=msg.data)
			await bot.send_message(chat_id=msg.from_user.id, text=f"Вы выбрали {user_product}")
			try:
				# Предлагает продукты если id строка совпадает
				await CookingReturn(msg.from_user.id, bot).run(bot=bot, msg=msg, id=cooking_ids)
			except IndexError:
				pass

	async def drop_product(self, msg, bot):
		if msg.text == "Очистить":
			UserModel(path='DataBase.db').update(user_id=msg.from_user.id, history="")
			await bot.send_message(chat_id=msg.from_user.id, text='Ваш список продуктов пуст.')


@dp.message_handler(content_types=['text'])
async def main(msg):
	await BotApp().start_menu(msg=msg, bot=bot)
	await ProductItems().product_type(msg=msg, bot=bot)
	await ProductItems().drop_product(msg=msg, bot=bot)
	await CookingReturn().cook(msg=msg, bot=bot)

@dp.callback_query_handler(lambda call: True)
async def callback(msg):
	await ProductItems().product_list(msg=msg, bot=bot)
	await ProductItems().add_product(msg=msg, bot=bot)


if __name__ == '__main__':
	executor.start_polling(dp)
