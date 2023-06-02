import socket 
import hashlib
import time
import pysftp
from vt_warning import vt_window
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.backends import default_backend

def key_exchange(key_size_var,tr_socket):
	'''
	Define el intercambio de claves.
	@param key_size_var: logitud de la clave
	@param tr_socket: soket para el intercambio
	@return: clave para descifrar, clave para cifrar
	''' 
	# Genera clave privada y clave publica RSA
	private_key = rsa.generate_private_key(public_exponent=65537,key_size=key_size_var,backend=default_backend())
	public_key = private_key.public_key()
	# Serializa clave publica en formato PEM
	public_key_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
	# Recibe clave pública del servidor
	server_public_key_pem = tr_socket.recv(512)
	server_public_key = serialization.load_pem_public_key(server_public_key_pem,backend=default_backend())	
	# Envia clave publica al servidor
	tr_socket.send(public_key_pem)	
	return private_key,server_public_key

def hash_file(file_name):
	'''
	Calcula hash SHA256 del fichero
	@param file_name: fichero
	@return: hash SHA256 del fichero
	''' 
	with open(file_name, "rb") as f: 
		# Lee archivo
		datos = f.read() 
		# Calcula hash SHA256 
		return hashlib.sha256(datos).hexdigest()

def send_cypher_msg(tr_socket,message,cypher_key):
	'''
	Envia mensaje cifrado
	@param tr_socket: socket para comunicacion
	@param message: mensaje a enviar
	@param cypher_key: clave con la que cifra
	''' 
	nombre_cifrado = cypher_key.encrypt(message,
	padding.OAEP(
			mgf=padding.MGF1(algorithm=hashes.SHA256()),
			algorithm=hashes.SHA256(),
			label=None
		))
	tr_socket.send(nombre_cifrado)

def recv_cypher_msg(rx_socket,buffer_size,decypher_key):
	'''
	Recibe mensaje y lo descifra
	@param rx_socket: socket para comunicacion
	@param buffer_size: longitud del buffer en recepcion
	@param decypher_key: clave con la que descifra
	@return: mensaje descifrado y decodificado
	''' 
	cypher_msg = rx_socket.recv(buffer_size)
	msg = decypher_key.decrypt(cypher_msg,
      padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
        )
      )
	return msg.decode('utf-8')

def sftp_transfer(_file,host,_port,user,_password):
	'''
	Transfiere por sftp un fichero
	@param _file: fichero a transferir
	@param host: IP para SFTP
	@param _port: puerto para SFTP
	@param user: Usuario SSH
	@param _password: Pass SSH
	''' 
	cnopts = pysftp.CnOpts()
	cnopts.hostkeys = None

	with pysftp.Connection(host, port=_port, username=user, password=_password, cnopts=cnopts) as sftp:
		with sftp.cd("."):
			sftp.put(_file)

			
def vt_check(transport_socket, private_key, server_public_key, buffer_size):
	'''
	Define comunicacion con el servidor CAPE, para la comprobacion en VT
	@param transport_socket: socket para la comunicacion
	@param private_key: Clave para descifrar
	@param server_public_key: Clave para cifrar
	@param buffer_size: longitud del buffer de recepcion
	''' 
	vt_msg = recv_cypher_msg(transport_socket,buffer_size,private_key)	
	vt_answer = str(vt_window(vt_msg))
	send_cypher_msg(transport_socket,vt_answer.encode(),server_public_key)




def send_CAPE(CAPE_ip,CAPE_port,tx_file):
	'''
	Define comunicacion con el servidor CAPE (intercambios de claves, sftp, VT)
	@param CAPE_ip: IP con a la que connectar socket
	@param CAPE_port: Puerto al que connectar socket
	@param tx_file: Fichero a transferir
	''' 
	# Definimos la longitud del buffer y de la clave
	buffer_size = 256
	key_size_var = buffer_size*8		
	# Crea un socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Conecta con el servidor
	s.connect((CAPE_ip, CAPE_port))
	# Generacion de clave privada e intercambio de claves publicas con el servidor
	private_key,server_public_key = key_exchange(key_size_var,s)
	# Envia el nombre del archivo
	nombre = tx_file.split("/")[len(tx_file.split("/"))-1]	
	send_cypher_msg(s,nombre.encode(),server_public_key)
  # Envia el hash del archivo
	file_hash = hash_file(tx_file)
	send_cypher_msg(s,file_hash.encode(),server_public_key)
  # Recibe credenciales para la transferencia sftp	
	sftp_credentials = recv_cypher_msg(s,buffer_size,private_key)	
	# Identifica user y pass para sftp
	user = sftp_credentials.split(":")[0]
	_pass = sftp_credentials.split(":")[1]
	# Realiza transferencia de archivo
	sftp_transfer(tx_file,"192.168.100.52",2205,user,_pass)
	# Se manda ACK para que el server procese el archivo
	s.send(b'ACK')
	# El host de CAPE nos envia un check con la comprobacion
	vt_check(s,private_key, server_public_key, buffer_size)
	s.close()
	print("Archivo enviado con éxito")

