import time
import os
from funciones import monitor_dir
import configparser

def run_auto(direct,config_file):
	'''
	Comienza monitorizacion.
	@param direct: Directorio a monitorizar
	@param config_file: Archivo de configuracion para la comunicacion
	''' 
	try:
		config = configparser.ConfigParser()
		config.read(str(config_file))
		cape_ip = str(config.get("analyzer","ip"))
		cape_port = int(config.get("analyzer","port"))
		monitor_dir(direct,cape_ip,cape_port)
	except KeyboardInterrupt:
		print("Se ha detenido el monitoreo manualmente.")  


