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

def parse_detail(program, handle):
	res = {handle: []}
	scopes = program['relationships']['structured_scopes']['data']
	for scope in scopes:
		t = {}
		try:
			t['id'] = scope['id']
			t['asset_type'] = scope['attributes']['asset_type']
			t['asset_identifier'] = scope['attributes']['asset_identifier']
			t['eligible_for_bounty'] = scope['attributes']['eligible_for_bounty']
			t['eligible_for_submission'] = scope['attributes']['eligible_for_submission']
			t['instruction'] = scope['attributes']['instruction']
			t['max_severity'] = scope['attributes']['max_severity']
			res[handle].append(t)
		except:
			res[handle].append(scope)
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

def get_details():
	prev={}
	try:
		prev = read_json_file('hackerone_details.json')
	except:
		pass
	handles = read_json_file('hackerone_pr.json').keys()
	for handle in handles:
		url = 'https://api.hackerone.com/v1/hackers/programs/' + handle
		res = get(url, auth=(USERNAME , TOKEN), headers = headers, proxies=proxies)
		if res.status_code==200:
			print(handle)
			detail = parse_detail(res.json(), handle)
			pd = prev.get(handle, False)
			if pd:
				if str(pd) == str(detail[handle]):
					continue
				else:
					for i in detail[handle]:
						if i not in pd:
							flag = False
							for j in pd:
								if j['id'] == i['id']:
									message = f'something had been changed in {handle}:\n From:\n'
									message += dumps(j, indent=4)
									message += '\n To:\n'
									message += dumps(i, indent=4)
									message += f'\n check here: https://hackerone.com/{handle}?type=team'
									tg.send_message(detail_target, message)
									flag = True
							if flag == False:
								message = f'assets added to {handle}:\n'
								message += dumps(i, indent=4)
								message += f'\n check here: https://hackerone.com/{handle}?type=team'
								tg.send_message(detail_target, message)		
			prev[handle] = detail[handle]
	write_json_file('hackerone_details.json', prev)


check_programs(fetch_programs())
get_details()

