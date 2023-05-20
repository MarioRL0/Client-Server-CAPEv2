import socket
import hashlib
import subprocess
from modulo_vt import analysis_vt
from cryptography.hazmat.primitives.asymmetric import padding,rsa
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.backends import default_backend


def hash_file(file_name):
  '''
  Obtiene hash de un archivo.
  @param file_name: archivo
  @return: hash del archivo
  '''
  with open(file_name, "rb") as f:
    # Lee los datos del archivo
    datos = f.read()
    # Calcula el hash con SHA256
    return hashlib.sha256(datos).hexdigest()

def key_exchange(key_size_var,tr_socket):
  '''
  Intercambio de claves.
  @param key_size_var: logitud de la clave
  @param tr_socket: socket para el intercambio
  @return: clave privada propia para descifrar y clave publica para cifrar
  '''  
  # Genera clave privada y clave publica
  private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=key_size_var,
    backend=default_backend()
  )
  public_key = private_key.public_key()
  # Serializa la clave pública en formato PEM
  public_key_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,format=serialization.PublicFormat.SubjectPublicKeyInfo)
  # Envia clave publica al cliente
  tr_socket.send(public_key_pem)
  # Recibe la clave pública del cliente y la serializa
  client_public_key_pem = tr_socket.recv(512)
  client_public_key = serialization.load_pem_public_key(client_public_key_pem,backend=default_backend())
  return private_key,client_public_key

def decypher_message(rx_socket,decypher_key,buffer_size):
  '''
  Recibe y descifra mensaje.
  @param rx_socket: socket que escucha
  @param decypher_key: clave con la que se descifra
  @param buffer_size: longitud del buffer de recepcion
  @return: mensaje decodificado y descifrado
  ''' 
  # Recibe el nombre del archivo cifrado
  cypher_msg = rx_socket.recv(buffer_size)
  # Descifra el nombre del archivo
  msg = decypher_key.decrypt(
    cypher_msg,
    padding.OAEP(
      mgf=padding.MGF1(algorithm=hashes.SHA256()),
      algorithm=hashes.SHA256(),
      label=None))
  return msg.decode('utf-8')

def cypher_message(tr_socket,cypher_key,message):
  '''
  Cifra y envia mensaje.
  @param tr_socket: socket para envio
  @param cypher_key: clave con la que cifra
  @param message: mensaje codificado (en bytes)
  ''' 
  # Cifra mensaje
  cypher_msg = cypher_key.encrypt(message,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    ))
  # Envia mensaje
  tr_socket.send(cypher_msg)

def wait_ack(rx_sock,buffer_size):
  '''
  Espera ACK.
  @param rx_sock: socket de escucha
  @param buffer_size: longitud del buffer de recepcion
  ''' 
  ack = rx_sock.recv(buffer_size)
  while not ack.startswith(b'ACK'):
      print("Espera ACK")
      ack = conn.recv(buffer_size)
  print("ACK recibido")

def change_zip(nombre):
  '''
  Cambia extension de un archivo a .zip .
  @param nombre: archivo a cambiar
  @return: archivo con .zip
  ''' 
  aux = nombre.split(".")
  aux[len(aux)-1] = "zip"
  return ".".join(aux)

def virus_total_check(transport_sock,private_key,client_public_key,buffer_size,file_name):
  '''
  Hace comprobacion preliminar con VT.
  @param transport_sock: socket para la comunicacion
  @param private_key: clave con la que cifra
  @param client_public_key: clave con la que descifra
  @param buffer_size:  longitud del buffer de recepcion
  @param file_name: potencial archivo a analizar con CAPE
  @return: Respuesta del cliente (mandar o no a CAPE el fichero)
  ''' 
  vt_result = analysis_vt("/home/xxx/" + file_name)
  cypher_message(transport_sock,client_public_key,vt_result.encode())
  client_respond = decypher_message(transport_sock,private_key,buffer_size)
  print(client_respond)
  if int(client_respond):
    return True
  else:
    return False

def run_server():
  '''
  Comportamiento del servidor
  '''
  # Crea socket
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # Asocia socket con interfaz ens18 y puerto 33033
  s.bind(("192.168.153.5", 33033))
  buffer_size = 256
  key_size_var = buffer_size*8
  while True:
    # Escucha conexiones
    s.listen()
    print("Escuchando …")
    # Acepta conexion
    conn, addr = s.accept()
    print(f"Conexion desde {addr}")
    # Crea sus claves y realiza intercambio de claves publicas con cliente
    private_key,client_public_key = key_exchange(key_size_var,conn)
    print("Public client key recibida")
    # Recibe nombre del archivo
    file_name = decypher_message(conn,private_key,buffer_size)
    # Recibe hash del archivo
    file_hash = decypher_message(conn,private_key,buffer_size)
    # Envia credenciales cifradas
    credenciales = "USER:PASSWORD"
    cypher_message(conn,client_public_key,credenciales.encode())
    # Espera ACK para procesar el fichero
    wait_ack(conn,buffer_size)
    print("Archivo recibido")
    # Se envia a cliente la respuesta de virustotal, para proceder segun se indique
    _analyse = virus_total_check(conn,private_key,client_public_key,buffer_size,file_name)
    # Si el cliente indica analisis, se procesa el fichero
    if _analyse:
      if file_hash == hash_file("/home/xxx/" + file_name):
        print("Hash verificado")
        # Procesa el fichero recibido
        #print(subprocess.run(["/root/servidor_auto/move_file.sh " + file_name + " " + change_zip(file_name)], shell=True))
        print(subprocess.run(["/root/servidor_auto/move_file.sh " + file_name], shell=True))
    # De lo contrario se elimina
    else:
      print(subprocess.run(["/root/servidor_auto/remove_file.sh " + file_name ], shell=True))
    # Cierra la conexion
    conn.close()


