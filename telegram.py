from requests import get
from dotenv import dotenv_values

class Telegram():

	def __init__(self):

		TOKEN = dotenv_values('.env')['TELEGRAM_API_KEY']
		self.baseUrl = f'https://api.telegram.org/bot{TOKEN}'
		self.is_up()

	def send_message(self, target, message):

		params = f'?chat_id={target}&text={message}'
		path = '/sendMessage'
		url = self.baseUrl + path + params
		try:
			get(url)
		except:
			pass

	def is_up(self):
		self.send_message("-1001886274384", "I'm up :)")



