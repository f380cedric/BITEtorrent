import socket

class Super:
	BUFFER_SIZE = 2048

	def __init__(self, name):
		self.name = name

	def receive(self,sock):
		data = bytes()
		while len(data) < 8:
			result = sock.recv(self.BUFFER_SIZE)
			data += result
			if not result:
				sock.close()
				print('Connection close')
				return False
		length = int(struct.unpack("!BBHL",data[0:8])[3])*4
		while len(data) < length:
			result = sock.recv(self.BUFFER_SIZE)
			data += result
			if not result:
				sock.close()
				print('Connection close')
				return False
		return data

	def start(self):
		""" Start the peers to listen to connection """
		print('Welcome\nSoftware developped by Pierre Baudoux, Cédric Hannotier, Mathieu Petitjean')
		print(self.__class__.__name__,'is launched as',self.name)

	@staticmethod
	def generate_error(error_code):
        """ Generate the ERROR message """
        ver = 1
        msg_type = 6
        msg_length = 3
        print(struct.pack("!BBHLHH",ver,msg_type,0,msg_length,error_code,0))
        return struct.pack("!BBHLHH",ver,msg_type,0,msg_length,error_code,0)

  	@staticmethod
    def check_message(message):
        """ Check if the message is valid """
        check_chunk = False
        if not len(message)%4:
            print('Multiple of 4 : OK')
        # Multiple of 4
            if struct.unpack("!BBHL",message[0:8])[0] == 1:
                print('Version is one : OK')
            # Version is one
                if (struct.unpack("!BBHL",message[0:8])[3]) == len(message)/4:
                    print('Correct size : OK')
                # body is correct size wrt msg_length
                    check_chunk = True
        return check_chunk

     @staticmethod
    def is_type(message, istype):
    	typedic = {'chunk_not_found':(6,4,2),'get_chunck':(4,3,7),'get_file_info':(2,3,2)}
    	config = typedic[istype]
        """ Check the request to see if it is a GET_CHUNK """
        return (struct.unpack("!BBHL",message[0:8])[1] == config[0]) & (struct.unpack("!BBHL",message[0:8])[config[1]] == config[2])
