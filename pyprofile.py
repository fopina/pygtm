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

	def connect(self, host, port, server_type, user, password):
		super(pyprofile, self).connect(host, port)

		self._svtyp = server_type

		# Acquire Token
		# TODO what is this message? (it simply works!)

		msg = '\x02\x34\x02\x31\x01\x01\x01\x01\x04\x03\x02\x35\x01'
		result = self.exchange_message(SERV_CLASS_SIGNON, msg)

		if result[0] == '1':
			raise Exception(result[1:])

		return

		# TODO unravel the rest of the fields...

		result_arr = self._unpack_lv2v(result)
		result_arr = self._unpack_lv2v(result_arr[0])
		result_arr = self._unpack_lv2v(result_arr[1])
		result_arr = self._unpack_lv2v(result_arr[1])
		self._token = result_arr[0]

		# signon message (to PBSNMSP)
		# (now it's all in the MTMJOURNAL...)

		msg = '\x025\x021\x13fopina JDBC driver!770e80cbe87d04efe5e01ab4f43c07f3\x01\x01\x16\x15\x025\x08PREPARE\x021\x06ICODE\x021\x01'
		result = self.exchange_message(SERV_CLASS_SIGNON, msg)
		print result

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
			'',
			str(self._msgid),
			'0',
			'',
		]

		if service_class != SERV_CLASS_SIGNON:
			msg_arr[1] = self._token

		msg_arr = [
			self._pack_v2lv(msg_arr),
			message,
		]

		msg += self._pack_v2lv(msg_arr)

		self._msgid += 1

		return super(pyprofile, self).exchange_message(msg)

	def _unpack_lv2v(self, packed_string):
		ret_array = []
		i = 0
		while i < len(packed_string):
			l = ord(packed_string[i])
			ret_array.append(packed_string[ i+1 : i+l ])
			i += l
		return ret_array

	def _pack_v2lv(self, unpacked_array):
		message = ''
		for s in unpacked_array:
			message += chr(len(s)+1) + s
		return message