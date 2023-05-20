import socket 
import hashlib
from cryptography.fernet import Fernet

#Funcion que genera en un archivo una clave simetrica, que garantiza la confidencialidad de nuestra comunicación 
# key_location --> Ruta al archivo donde se guarda la llave
 
def key_gen(key_location):
	# Generar una clave simétrica y guardarla en un archivo
	clave = Fernet.generate_key() 
	with open(key_location, "wb") as f: 
		f.write(clave)
#Funcion que genera hash del nombre del archivo, que garantiza la integridad de la transmision

def hash_file(file_name):
	with open(file_name, "rb") as f: 
		# Leer los datos del archivo 
		datos = f.read() 
		# Calcular el hash con SHA256 
		hashed = hashlib.sha256(datos).hexdigest() 
	return hashed
		
def transfer_file(key_generated,key_hash,archivo):

	with open(key_generated, "rb") as f:
		clave = f.read()
	# Crear un objeto Fernet con la clave
	fernet = Fernet(clave)


	# Crear un socket TCP
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Conectarse al servidor en la dirección 192.168.153.5 y puerto 33033
	s.connect(("192.168.153.5", 33033))

	# Leer el nombre del archivo a enviar

	# Enviar el nombre del archivo cifrado al servidor
	nombre = archivo.split("/")[len(archivo.split("/"))-1]
	nombre_cifrado = fernet.encrypt(nombre.encode()) 
	s.send(nombre_cifrado)

  # Enviar el hash del archivo
	hash_archivo = hash_file(archivo)
	hash_archivo_cifrado = fernet.encrypt(hash_archivo.encode())
	s.send(hash_archivo_cifrado)

	# Abrir el archivo en modo binario
	print(nombre)
	print(hash_archivo)
	with open(archivo, "rb") as f: 
		# Leer los datos del archivo 
		datos = f.read() 
	# Cifrar los datos con la clave 
	datos_cifrados = fernet.encrypt(datos) 
	print(datos_cifrados)
	# Enviar los datos cifrados al servidor 
	s.send(datos_cifrados)

	# Cerrar el socket
	s.close()

	print("Archivo enviado con éxito")

#key_gen("/home/xxx/Desktop/Scripts_auto/clave_hash.txt")
transfer_file("/home/xxx/Desktop/Scripts_auto/clave.txt","/home/xxx/Desktop/Scripts_auto/clave_hash.txt","/home/xxx/Desktop/Scripts_auto/transferir_imagen.jpeg")
