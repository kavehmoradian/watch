from sqlite3 import connect


class DbHelper():

	def __init__(self, dbname):

		self.conn = connect(dbname, check_same_thread=False)
		self.cur = self.conn.cursor()
		self.setup()

	def setup(self):

		programs = '''CREATE TABLE IF NOT EXISTS programs(
					id INTEGER PRIMARY KEY,
					type VARCHAR(30),
					handle VARCHAR(30),
					name VARCHAR(30),
					submission_state VARCHAR(30),
					state VARCHAR(30),
					offers_bounties VARCHAR(5)
					)'''
		program_detail = '''CREATE TABLE IF NOT EXISTS program_detail(
					id INTEGER PRIMARY KEY,
					handle INTEGER,
					data TEXT	
					)'''
		self.cur.execute(programs)
		self.cur.execute(program_detail)
		self.conn.commit()

	def add_program(self, data):

		stmt = '''INSERT INTO programs(id, type, handle, name,
				submission_state, state, offers_bounties)
				VALUES({},"{}","{}","{}","{}","{}","{}")'''
		stmt = stmt.format(data['id'], data["type"], data['handle'], data['name'],
					data['submission_state'], data['state'], data['offers_bounties'])
		self.cur.execute(stmt)
	
	def check_program_exists(self, id):
		
		stmt = 'SELECT * FROM programs WHERE id={}'.format(id)
		self.cur.execute(stmt)
		return len(self.cur.fetchall())

	def program_data(self, id):

		stmt = 'SELECT * FROM programs WHERE id={}'.format(id)
		self.cur.execute(stmt)
		return self.cur.fetchall()[0]

	def update_program(self, data):
		
		stmt = 'DELETE FROM programs WHERE id={}'.format(data['id'])
		self.cur.execute(stmt)
		self.add_program(data)

	def commit(self):
		self.conn.commit()

