from requests import get
from dotenv import dotenv_values
from dbhelper import DbHelper
from telegram import Telegram
from subscribers import subscribers
from json import dumps

proxies = {
            'http': 'socks5://127.0.0.1:9090',
            'https': 'socks5h://127.0.0.1:9090'
          }
headers = {
  'Accept': 'application/json'
}
TOKEN = dotenv_values('.env')['HACKERONE_API_KEY']
USERNAME = dotenv_values('.env')['HACKERONE_USERNAME']
db = DbHelper('hackerone.db')
tg = Telegram()
programs_target = subscribers['watch2']


def send_program_diff(prev, now):
	prev_d = {}
	prev_d['id'] = prev[0]
	prev_d['type'] = prev[1]
	prev_d['handle'] = prev[2]
	prev_d['name'] = prev[3]
	prev_d['submission_state'] = prev[4]
	prev_d['state'] = prev[5]
	prev_d['offers_bounties'] = prev[6]
	handle = now['handle']
	message = 'a program had been edited:\nform: \n'
	message += dumps(prev_d, indent=4) + '\nto: \n'
	message += dumps(now, indent=4)
	message += f'\nmore detail: https://hackerone.com/{handle}?type=team'
	tg.send_message(programs_target, message)

def fetch_programs():
	url = "https://api.hackerone.com/v1/hackers/programs?page[size]=100&page[number]=1"
	programs = []
	while url:
		reslut = get(url, auth=(USERNAME , TOKEN), headers = headers, proxies=proxies)
		programs += reslut.json()['data']
		url = reslut.json()['links'].get('next', False)
		break
	return programs

def add_programs(programs):
	for program in programs:
		data = {}
		data['id'] = int(program['id'])
		data['type'] = program['type']
		data['handle'] = program['attributes']['handle']
		data['name'] = program['attributes']['name']
		data['submission_state'] = program['attributes']['submission_state']
		data['state'] = program['attributes']['state']
		data['offers_bounties'] = str(program['attributes']['offers_bounties'])
		if db.check_program_exists(data['id']):
			prev = db.program_data(data['id'])
			if tuple(data.values()) == prev:
				continue
			else:
				send_program_diff(prev, data)
				db.update_program(data)
		else:
			db.add_program(data)
			handle = data['handle']
			message = 'new program just added to hackerone:\n'
			message += dumps(data, indent=4)
			message += f'\n check here: https://hackerone.com/{handle}?type=team'
			tg.send_message(programs_target, message)
		db.commit()
		return


# TOKEN="Dj3hOarlVe0W1am5krVrA3tCtz/4X58UCVO80PKqtDA="
# USERNAME="kaveh4me"
#url = "https://api.hackerone.com/v1/hackers/programs/hyatt"
#600 req per min

add_programs(fetch_programs())




