from requests import get
from dotenv import dotenv_values
from subscribers import subscribers

class Telegram():

	def __init__(self):

		TOKEN = dotenv_values('.env')['TELEGRAM_API_KEY']
		self.baseUrl = f'https://api.telegram.org/bot{TOKEN}'

	def send_message(self, target, message):
		#debug only:
		proxies = {
            'http': 'socks5://127.0.0.1:9090',
            'https': 'socks5h://127.0.0.1:9090'
          }

		params = f'?chat_id={target}&text={message}'
		path = '/sendMessage'
		url = self.baseUrl + path + params
		try:
			get(url, proxies=proxies)
		except:
			pass

	def is_up(self):
		self.send_message(subscribers['watch1'], "Main Script: I'm up :)")



