import socket
import struct

class pymtm():
	def __init__(self):
		self._socket = socket.socket()
		self._endianess = '!h'

	'''
	From struct documentation:
	http://docs.python.org/2/library/struct.html
	Section 7.3.2.1

	<	little-endian
	>	big-endian
	!	network (= big-endian)

	'''
	def set_endianess(self, struct_signal):
		if struct_signal in '<>':
			self._endianess = struct_signal + 'h'
		else:
			self._endianess = '!h'

	def connect(self, host, port):
		self._socket.connect((host, port))

	def exchange_message(self, message):
		message_to_send = _message_header(len(message)) + message
		self._socket.send(message_to_send)

	def _message_header(self, message_length):
		return struct.pack(self._endianess, message_length + 2)

