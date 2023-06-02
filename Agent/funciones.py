import os
import time
from client_definitivo import send_CAPE

def list_directory(path,onlylist):
	'''
	Crea lista con nombre de archivos y fecha en la que se unieron al sistema.
	@param path: ruta del archivo a analizar
	@param onlylist: Determinar el formato de la salida
	@return: lista creada de archivos y fechas del directorio, longitud de la lista creada
	''' 
	if onlylist:
		# Creamos lista con estructura [(file0,date_file0),(file1,date_file1),...]
		file_list = [(file_name, os.path.getmtime(os.path.join(path, file_name))) for file_name in os.listdir(path)]
		return file_list,len(file_list)
	# En este caso se devuelve solo la lista
	else:
		file_list = [(file_name, os.path.getmtime(os.path.join(path, file_name))) for file_name in os.listdir(path)]   
		return file_list
	
def new_file(directory_list):
	'''
	Ordena por fecha y selecciona el archivo mas reciente.
	@param directory_list: lista del directorio que se analiza
	@return: nombre del fichero mas reciente
	'''  
	directory_list.sort(key=lambda x: x[1], reverse=True)
	return directory_list[0][0]

def wait_download(file_name,monitor_dir,len_compare):
	'''
	Espera a que se descargue el archivo. Archivo .part es un archivo preliminar en una descarga
	@param file_name: lista del directorio que se analiza
	@param monitor_dir: lista del directorio que se analiza
	@param len_compare: Longitud de la carpeta con la que compara si
	@return: nombre del fichero mas reciente, orden de upload
	'''  
	upload = True
	while file_name[-5:] == ".part" or file_name[-11:] == ".crdownload" or file_name[-4:] == ".tmp":
		print("Identifica .part")
		time.sleep(2)
		file_list_aux = list_directory(monitor_dir,False)
		file_name = new_file(file_list_aux)
		if len_compare >= len(file_list_aux): upload = False
		else: upload = True
	return file_name,upload


def monitor_dir(direct,cape_ip,cape_port):
	'''
	Monitoriza directorio indicado y se comunica con host de CAPE.
	@param direct: directorio a monitorizar
	@param cape_ip: IP para conectar con el socket que abre el host de CAPE
	@param cape_port: Puerto para conectar con el socket que abre el host de CAPE
	'''  
	print("Escuchando en Carpeta: ") 
	# Directorio a monitorizar
	monitor_dir = str(direct)
	# Lista con los nombres de los archivos y tiempo que indica su ultima modificacion
	file_list, len_compare = list_directory(monitor_dir,True)
	# Se obtiene tiempo de referencia para comparar las modificaciones en el directorio actual
	t0 = os.path.getmtime(os.path.join(monitor_dir))
	while True:
		# Cadencia de monitoreo    
		time.sleep(1)
		# Compara si se ha modificado la carpeta
		if t0 < os.path.getmtime(os.path.join(monitor_dir)):
			print("Carpeta modificada")
			# Actualiza la fecha en la que esta carpeta se ha modificado 
			t0 = os.path.getmtime(os.path.join(monitor_dir))
			# Obtiene una lista con nombres de los archivos y tiempo que indica su ultima modificacion
			file_list = list_directory(monitor_dir,False)
			# Compara si el directorio tiene algun archivo nuevo    
			if len_compare < len(file_list):
				# Compara que el archivo no finalice en .part, ya que eso indica que la descarga no se ha finalizado
				file_name = new_file(file_list)
				# Espera a que .part desaparezca o en el caso de que desaparezca, pero no se descargue nada upload es false
				file_name,upload = wait_download(file_name,monitor_dir,len_compare)
				if upload:
					print("Se ha detectado un nuevo archivo: " + str(file_name))
					# Cadena de la ubicacion del archivo
					tx_file = monitor_dir + "/" + str(file_name)
					# Envia al host de CAPE el archivo
					send_CAPE(cape_ip,cape_port,tx_file)
			# Actualiza longitud del directorio
			len_compare = len(file_list)
