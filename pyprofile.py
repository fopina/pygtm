from pymtm import pymtm
import time

SERV_CLASS_SIGNON = '0'
SERV_CLASS_SQL    = '5'
SERV_CLASS_MRPC   = '3'

class pyprofile(pymtm):

	def __init__(self):
		pymtm.__init__(self)
		self._token = None
		self._svtyp = None
		self._msgid = 0
		self.max_rows = 30

	def connect(self, host, port, server_type, user, password):
		super(pyprofile, self).connect(host, port)

		self._svtyp = server_type

		# Sign on (and acquire token)
		'''
		#define srv_prc   0
		#define user_id   1
		#define stn_id    2
		#define user_pwd  3
		#define inst_id   4
		#define fap_ids   5
		#define context   6
		'''

		msg_arr = [
			'1',
			user,
			'nowhere', # TLO
			password,
			'',
			'',
			'\x15\x025\x06ICODE\x021\x08PREPARE\x023', # context
		]

		result = self.exchange_message(SERV_CLASS_SIGNON, self._pack_v2lv(msg_arr))

		result_arr = self._check_error(result)

		self._token = result_arr[0]

	def executeSQL(self,query,*args):
		cursor_id = 0
		final_sql = ''
		if query[:6].lower() == 'select':
			cursor_id = int(time.time())
			final_sql = 'OPEN CURSOR %d AS %s' % (cursor_id, query)
		else:
			final_sql = query


		sql_modifiers = '/ROWS=%d' % self.max_rows

		# Replace "?" with host variables
		# TODO desperate need of actual parsing and validation
		# TODO INSERT ... VALUES (?,?,?...) are not covered
		if len(args) > 0:
			host_variables = []
			temp_sql = final_sql.replace('=?','= ?')
			final_sql = ''
			i = temp_sql.find('= ?')
			old_i = 0
			variable_id = 1
			while i > -1:
				variable_str = 'C%d' % variable_id
				final_sql += temp_sql[old_i : i] + '= :' + variable_str
				old_i = i + 3
				try:
					host_variables.append('%s=\'%s\'' % (variable_str, args[variable_id - 1]))
				except IndexError:
					raise Exception('VAL_ERROR','More markers than variables')
				variable_id += 1
				i = temp_sql.find('= ?',old_i)

			if variable_id != (len(args) + 1):
				raise Exception('VAL_ERROR','More variables than markers')

			sql_modifiers += '/USING=(%s)' % ','.join(host_variables)

		msg_arr = [
			final_sql, # query
			sql_modifiers,
			'', # ?
		]

		result = self.exchange_message(SERV_CLASS_SQL, self._pack_v2lv(msg_arr))

		result_arr = self._check_error(result)

		count = result_arr[2]

		result = result_arr[3].split('\r\n')

		types = list(result_arr[5].split('|')[0])

		if cursor_id > 0:
			msg_arr = [
				'CLOSE %d' % cursor_id, # query
				'',
				'',
			]
			# ignored
			_ = self.exchange_message(SERV_CLASS_SQL, self._pack_v2lv(msg_arr))


		return (result,types)

	def exchange_message(self, service_class, message):
		# MTM header
		msg = self._svtyp + '\x1c'

		# Message Header
		'''
		From libsql.h (for reference):
		#define srv_cls   0
		#define token     1
		#define msg_id    2
		#define stf_flg   3
		#define grp_recs  4
		'''

		msg_arr = [
			service_class,
			self._token,
			str(self._msgid),
			'0',
			'',
		]

		if service_class == SERV_CLASS_SIGNON:
			msg_arr[1] = ''

		msg_arr = [
			self._pack_v2lv(msg_arr),
			message,
		]

		msg += self._pack_v2lv(msg_arr)

		self._msgid += 1

		return super(pyprofile, self).exchange_message(msg)

	def _check_error(self, packed_string):
		if packed_string[0] != '0':
			raise Exception('MTM_ERROR',packed_string[1:])

		result_arr = self._unpack_lv2v(packed_string[1:])
		result_arr = self._unpack_lv2v(result_arr[1])
		error_code = result_arr[0]
		result_arr = self._unpack_lv2v(result_arr[1]) # one extra unpack for both error handling and normal flow
		if error_code != '0':
			raise Exception(result_arr[2],result_arr[4])
		return result_arr

	def _unpack_lv2v(self, packed_string):
		ret_array = []
		i = 0
		while i < len(packed_string):
			l = ord(packed_string[i])
			if l == 0:
				i += 1
				continue
			ret_array.append(packed_string[ i+1 : i+l ])
			i += l
		return ret_array

	def _pack_v2lv(self, unpacked_array):
		message = ''
		for s in unpacked_array:
			message += chr(len(s)+1) + s
		return message