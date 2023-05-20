import socket
import hashlib
from cryptography.fernet import Fernet

# Leer la clave simétrica del archivo
with open("/root/servidor_auto/clave.txt", "rb") as f: 
  clave = f.read()

# Crear un objeto Fernet con la clave
fernet = Fernet(clave)

# Crear un socket TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Asignar la dirección 192.168.153.5 y puerto 33033 al socket
s.bind(("192.168.153.5", 33033))
while True:
  # Escuchar conexiones entrantes
  s.listen()

  print("Esperando conexiones…")

  # Aceptar una conexión de un cliente
  conn, addr = s.accept()

  print(f"Conectado con {addr}")

  # Recibir el nombre del archivo cifrado del cliente
  nombre_cifrado = conn.recv(1024)
  # Descifrar el nombre del archivo con la clave
  nombre = fernet.decrypt(nombre_cifrado).decode()
  print(nombre)

  # Recibir el nombre del archivo cifrado del cliente
  hash_cifrado = conn.recv(256)
  # Descifrar el nombre del archivo con la clave
  hash_descifrado = fernet.decrypt(hash_cifrado)
  print(hash_descifrado)

  # Abrir un archivo con el mismo nombre en modo binario
  with open("/root/servidor_auto/files/" + nombre, "wb") as f:
    # Recibir los datos cifrados del cliente
    datos_cifrados = conn.recv(8201)
    # Descifrar los datos con la clave
    print(datos_cifrados) 
    datos = fernet.decrypt(datos_cifrados)
    # Escribir los datos en el archivo
    f.write(datos)
    # Cerrar la conexión

  conn.close()
  print("Archivo recibido con éxito")

  if hash_descifrado == hashlib.sha256("/root/servidor_auto/files/" + nombre).hexdigest():
    print("Hash verificado")
  else:
    print("La verificacion de integridad del archivo ha fallado desde {addr} ,contacte con el usuario correspondiente a ese equipo")
