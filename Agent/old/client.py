import socket 
import hashlib
import time
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.backends import default_backend

# Funcion que genera hash del nombre del archivo, que garantiza la integridad de la transmision
# file_name --> ubicacion del archivo

def hash_file(file_name):
	with open(file_name, "rb") as f: 
		# Lee archivo
		datos = f.read() 
		# Calcula hash SHA256 
		hashed = hashlib.sha256(datos).hexdigest() 
	return hashed

# Funcion que envia por bloques el archivo a analizar
# transport_socket --> socket que se haya establecido con el servidor
# filename --> ubicacion del archivo
# server_public_key --> clave publica que el servidor nos ha transferido

def send_file_blocks(transport_socket,filename, server_public_key,buffer_size):
	with open(filename, "rb") as f:
		# Lee el archivo en bloques de 128 bytes
		i = 1
		while True:
			print("Iteracion " + str(i))
			i += 1
			datos = f.read(int(buffer_size/2))			
			if not datos:
				break
			# Cifrar el bloque de datos
			datos_cifrados = server_public_key.encrypt(datos, 
				padding.OAEP(
				  mgf=padding.MGF1(algorithm=hashes.SHA256()),
				  algorithm=hashes.SHA256(),
				  label=None
				)
			)
			# Enviar el bloque cifrado al servidor
			transport_socket.send(datos_cifrados)
		
def transfer_file(archivo):
	buffer_size = 256
	key_size_var = buffer_size*8
	# Generar una clave privada y pública RSA
	private_key = rsa.generate_private_key(public_exponent=65537,key_size=key_size_var,backend=default_backend())
	public_key = private_key.public_key()
	# Serializar la clave pública en formato PEM
	public_key_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
	
	# Crear un socket TCP
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Conectarse al servidor en la dirección 192.168.153.5 y puerto 33033
	print("Conectando... ")
	s.connect(("192.168.153.5", 33033))
	print("Conecto ")
	# Recibir la clave pública del servidor
	server_public_key_pem = s.recv(512)
	# Envio clave publica al servidor
	s.send(public_key_pem)
	
	print("Recibo: " + str(server_public_key_pem))
  

	server_public_key = serialization.load_pem_public_key(server_public_key_pem,backend=default_backend())
	# Leer el nombre del archivo a enviar

	# Enviar el nombre del archivo cifrado al servidor
	nombre = archivo.split("/")[len(archivo.split("/"))-1]
	print("Se cifra con longitud " + str(len(nombre.encode())))
	nombre_cifrado = server_public_key.encrypt(nombre.encode(),
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )) 
	s.send(nombre_cifrado)

  # Enviar el hash del archivo
	hash_archivo = hash_file(archivo)
	print("Se cifra con longitud " + str(len(hash_archivo.encode())))
	hash_archivo_cifrado = server_public_key.encrypt(hash_archivo.encode(),
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )) 
	s.send(hash_archivo_cifrado)
	'''
	# Abrir el archivo en modo binario
	print(nombre)
	print(hash_archivo)
	send_file_blocks(s,archivo, server_public_key,buffer_size)
	# Cerrar el socket
	s.close()
	'''
	
	print("Archivo enviado con éxito")

start_time = time.time()
transfer_file("/home/xxx/Desktop/Scripts_auto/transferir_imagen.jpeg")
#transfer_file("/home/xxx/Downloads/vlc-3.0.18-win32.exe")
end_time = time.time()
elapsed_time = end_time - start_time
print("Tiempo de ejecución: {:.6f} segundos".format(elapsed_time))
