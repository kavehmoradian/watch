from requests import get
from dotenv import dotenv_values
from telegram import Telegram
from subscribers import subscribers
from json import dumps, loads
from jsondiff import diff

proxies = {
            'http': 'socks5://127.0.0.1:9090',
            'https': 'socks5h://127.0.0.1:9090'
          }
headers = {
  'Accept': 'application/json'
}
TOKEN = dotenv_values('.env')['HACKERONE_API_KEY']
USERNAME = dotenv_values('.env')['HACKERONE_USERNAME']
tg = Telegram()
programs_target = subscribers['watch2']
detail_target = subscribers['watch3']

def read_json_file(file):
	with open(file, 'r') as f:
		return loads(f.read())

def write_json_file(file, data):
	with open(file, 'w') as f:
		d = dumps(data, indent=4)
		f.write(d)


def send_program_diff(prev, now, handle):
	message = handle + ' had been edited:\nForm: \n'
	message += dumps(prev, indent=4) + '\nTo: \n'
	message += dumps(now, indent=4)
	message += f'\nmore detail: https://hackerone.com/{handle}?type=team'
	tg.send_message(programs_target, message)

def parse_programs(programs):
	res = {}
	for program in programs:
		handle = program['attributes']['handle']
		data = {'name': program['attributes']['name'], 
					'submission_state': program['attributes']['submission_state'],
					'offers_bounties': program['attributes']['offers_bounties']}
		res[handle] = data
	return res

def fetch_programs():
	url = "https://api.hackerone.com/v1/hackers/programs?page[size]=100&page[number]=1"
	programs = []
	while url:
		result = get(url, auth=(USERNAME , TOKEN), headers = headers, proxies=proxies)
		programs += result.json()['data']
		url = result.json()['links'].get('next', False)
	return parse_programs(programs)

def check_programs(programs):
	prev={}
	try:
		prev = read_json_file('hackerone_pr.json')
	except:
		pass
	for handle, data in programs.items():
		obj = prev.get(handle, False)
		if obj:
			if str(obj) == str(data):
				continue
			else:
				send_program_diff(obj, data, handle)
		else:
			message = 'new program just added to hackerone:\n'
			message += dumps(data, indent=4)
			message += f'\n check here: https://hackerone.com/{handle}?type=team'
			tg.send_message(programs_target, message)
	write_json_file('hackerone_pr.json', programs)

# def get_details():
# 	handles = db.get_handles()
# 	for i in handles:
# 		handle = i[0]
# 		url = 'https://api.hackerone.com/v1/hackers/programs/' + handles[0][0]
# 		res = get(url, auth=(USERNAME , TOKEN), headers = headers, proxies=proxies)
# 		d = res.json()
# 		data = {}
# 		data['id'] = str(d['id'])
# 		data['handle'] = d['attributes']['handle']
# 		data['data'] = d['relationships']['structured_scopes']['data']
# 		if db.check_detail_exists(d['id']):
# 			prev = db.get_detail(data['id'])
# 			print(prev[2])
# 			print(data['data'])
# 			if str(data['data'])==str(prev[2]):
# 				continue
# 				print("same")
# 			else:
# 				db.update_detail(data)

# 		else:
# 			db.add_detail(data)
# 			handle = data['handle']
# 			message = 'new program just added to hackerone.\n details:\n'
# 			message += dumps(data, indent=2)
# 			message += f'\n check here: https://hackerone.com/{handle}?type=team'
# 			tg.send_message(detail_target, message)
# 		db.commit()
# 		return


#get_details()
#add_programs(fetch_programs())
check_programs(fetch_programs())


