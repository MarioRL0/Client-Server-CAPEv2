import socket
import hashlib
from cryptography.hazmat.primitives.asymmetric import padding,rsa
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.backends import default_backend

#Funcion para obtener hash de un archivo
def hash_file(file_name):
  with open(file_name, "rb") as f:
    # Lee los datos del archivo
    datos = f.read()
    # Calcula el hash con SHA256
    hashed = hashlib.sha256(datos).hexdigest()
  return hashed

# Socket TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Socket en interfaz ens18 y puerto 33033
s.bind(("192.168.153.5", 33033))

while True:
  buffer_size = 256
  key_size_var = buffer_size*8
  # Clave privada y pública RSA
  private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=key_size_var,
    backend=default_backend()
  )
  public_key = private_key.public_key()

  # Serializar la clave pública en formato PEM
  public_key_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)

  # Escuchar conexiones
  s.listen()

  print("Escuchando …")

  # Acepta conexion
  conn, addr = s.accept()

  print(f"Conexion desde {addr}")

  # Envia clave publica al cliente
  conn.send(public_key_pem)

  # Recibe el nombre del archivo cifrado
  nombre_cifrado = conn.recv(buffer_size)
  # Descifra el nombre del archivo
  nombre = private_key.decrypt(
    nombre_cifrado,
    padding.OAEP(
      mgf=padding.MGF1(algorithm=hashes.SHA256()),
      algorithm=hashes.SHA256(),
      label=None)).decode('utf-8')
  # Recibe el hash del archivo cifrado del cliente
  hash_cifrado = conn.recv(buffer_size)
  # Descifra el hash del archivo
  hash_descifrado = private_key.decrypt(hash_cifrado,padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),algorithm=hashes.SHA256(),label=None)).decode('utf-8')


  # Se abre archivo en la carpeta files, que es donde vamos a almacenar los archivos que lleguen
  with open("/root/servidor_auto/files/" + nombre, "wb") as f:
    # Descifrar los datos por bloques
    datos = b""
    i = 1
    while True:
      print("Iteracion: " + str(i))
      i += 1
      datos_cifrados = conn.recv(buffer_size)
      # Para de descifrar si no se reciben datos
      if not datos_cifrados:
        break
      # Por si no se llena el buffer
      while (len(datos_cifrados)!=buffer_size):
        datos_cifrados += conn.recv(buffer_size-len(datos_cifrados))
      print("Longitud de datos_cifrados " + str(len(datos_cifrados)))
      # Para de descifrar si no se reciben datos
      datos += private_key.decrypt(datos_cifrados,
      padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
        )
      )
      # Envio ACK para evitar un reseteo de conexion
      #ack_msg = b''
      #conn.send(ack_msg)

    # Escribe los datos en el archivo
    f.write(datos)
  # Cierra la conexion
  conn.close()
  print("Archivo recibido")
  if hash_descifrado == hash_file("/root/servidor_auto/files/" + nombre):
    print("Hash verificado")
  else:
    print("La verificacion de integridad del archivo ha fallado desde {addr} ,contacte con el usuario correspondiente a ese equipo")
