import socket
import struct

class pymtm(object):
	'''
	svtype 
	'''
	def __init__(self, server_type = None):
		self._socket = socket.socket()
		self._server_type = server_type
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

	def close(self):
		self._socket.close()

	def exchange_message(self, message):
		self.send_message(message)
		return self.read_message()

	def send_message(self, message):
		if self._server_type:
			message = self._server_type + '\x1c' + message

		header = struct.pack(self._endianess, len(message) + 2)
		message_to_send = header + message
		self._socket.send(message_to_send)

	def read_message(self):
		len_str = self._socket.recv(2)
		if not len_str : return None
		length = struct.unpack(self._endianess, len_str)[0]
		length -= 2
		message = ''
		read_count = 0
		while read_count < length:
			read_block = min(length - read_count,1024)
			partial_message = self._socket.recv(read_block)
			read_count += len(partial_message)
			if not partial_message : break
			message += partial_message
		return message