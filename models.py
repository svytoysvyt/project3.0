from sqlite3 import connect


class Model:
	def __init__(self, path: str):
		self.path = path

	def _connect(self):
		return connect(database=self.path)
	
	def product_type(self):
		query = 'select тип FROM  продукты;'
		connect = self._connect()
		cursor = connect.cursor()
		# Отправка запроса и закрытие соединения
		row = cursor.execute(query)
		rows = [x[0] for x in row.fetchall()]
		cursor.close()
		connect.close()
		return set(rows)

	def product(self, product_type=''):
		"""
		Если product_type равен None, то ищем только тип продукта
		Иначе название, по типу.
		"""
		if len(product_type) > 1 and product_type != "all":
			query = f'select id, название FROM  продукты WHERE тип="{product_type}";'
		else:
			query = f'select id FROM  продукты;'

		connect = self._connect()
		cursor = connect.cursor()
		# Отправка запроса и закрытие соединения
		row = cursor.execute(query)

		rows = []
		for x in row.fetchall():
			if product_type == "all":
				rows.append(x[0])
			else:
				rows.append(x[:])

		cursor.close()
		connect.close()
		return rows

	def product_name(self, ids=None) -> str:
		query = f'select название FROM продукты WHERE id="{ids}";'
		connect = self._connect()
		cursor = connect.cursor()
		# Отправка запроса и закрытие соединения
		row = cursor.execute(query)
		rows = [x[0] for x in row.fetchall()]
		cursor.close()
		connect.close()
		return rows[0]

	def cooke(self):
		query = f'select * FROM  блюда;'
		connect = self._connect()
		cursor = connect.cursor()
		# Отправка запроса и закрытие соединения
		row = cursor.execute(query)

		rows = [x for x in row.fetchall()]
		cursor.close()
		connect.close()
		return rows


class UserModel(Model):
	def __init__(self, path: str):
		super().__init__(path)

	'''
		//Выборка только истории
		SELECT history FROM user_history WHERE user_id={user_id};
		//Добавление юзера при == /start
		INSERT INTO user_history(user_id, history) VALUES();
		//Обновление истории выбранных ключей
		UPDATE user_history  SET history='' WHERE user_id={user_id};
	'''

	def create_user(self, user_id:int):
		query = f'INSERT INTO user_history(user_id) VALUES({user_id});'
		connect = self._connect()
		cursor = connect.cursor()
		cursor.execute(query)
		connect.commit()
		cursor.close()
		return connect.close()

	def update(self, user_id:int, history:str):
		query = f'UPDATE user_history  SET keys="{history}" WHERE user_id={user_id};'
		connect = self._connect()
		cursor = connect.cursor()
		cursor.execute(query)
		connect.commit()
		cursor.close()
		return connect.close()
	
	def show(self, user_id:int):
		query = f'SELECT keys FROM user_history WHERE user_id={user_id};'
		connect = self._connect()
		cursor = connect.cursor()
		row = cursor.execute(query)
		rows = [x for x in row.fetchall()]
		cursor.close()
		connect.close()
		return rows[0][0]