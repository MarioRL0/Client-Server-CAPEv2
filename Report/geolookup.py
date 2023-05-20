import os
import json
import requests
import time

from lib.cuckoo.common.abstracts import Report
from lib.cuckoo.common.exceptions import CuckooReportError

class Geolookup(Report):
		"""Report de conexiones red"""
    
		def default(self, obj):
			if isinstance(obj, bytes):
				return obj.decode()
			raise TypeError
  
		def geo_loc(self,ip):
			'''
			@param ip: IP a geolocalizar
			@return: longitud y latitud de la IP
			'''
			time.sleep(0.03)
			# URL para la API, la API key es de pago
			request_url = 'http://ip-api.com/json/' + ip
			# Envia request
			response = requests.get(request_url)
			# Comprueba que tiene respuesta
			if response.status_code == 200:
				# Decodifica resultado de la respuesta
				result = response.content.decode()
			# Si respuesta no es 200 se duerme 1 min, ya que el rate limit de esta API es 45 pet/min
			else:
				time.sleep(60)
				# Repite request
				response = requests.get(request_url)
				# Decodifica resultado de la respuesta
				result = response.content.decode()		
			# Carga en JSON el resultado
			result  = json.loads(result)
			# Comprueba que la direccion no este en un rango reservado
			if "message" in result:
				if result["message"] == "reserved range":
					# Si esta en rango reservado devuelve 0,0
					return ["",""]
			# Devuelve longitud y latitud de la IP
			else:
				return [result["lon"],result["lat"]]

		def check_dup(self,coor_dicc,ip):
			if str(ip) not in coor_dicc:
				coor_dicc[str(ip)] = self.geo_loc(ip)
			return coor_dicc,coor_dicc[str(ip)]

		def run(self, resultados: dict):
			#try:
				#r_path = str(self.analysis_path)+  "/logs/eve.json"
				coor_dicc = {}
				r_path = os.path.join(self.analysis_path, "logs/eve.json")
				#print(r_path)
				with open(r_path, 'r') as f:
					data = f.readlines()  # Leer el archivo y dividirlo en una lista de líneas
				result = []
				for line in data:
					obj = json.loads(line.strip())  # Convertir cada línea en un diccionario de Python
					# ID del analisis
					#print(os.path.join(self.analysis_path))
					obj["analysis_id"] = resultados["info"]["id"]
					if "src_ip" in obj:
						if int(obj["src_ip"].split(".")[0])!=192:
							coor_dicc,obj["geo_src"] = self.check_dup(coor_dicc,str(obj["src_ip"]))  # Agregar el campo "src_geo"
						else:
							obj["geo_src"] = [-0.87,41.65]
						if int(obj["dest_ip"].split(".")[0])!=192:
							coor_dicc,obj["geo_dst"] = self.check_dup(coor_dicc,str(obj["dest_ip"]))  # Agregar el campo "dest_geo"
						else:
							obj["geo_dst"] = [-0.87,41.65]
						result.append(obj)  # Agregar el objeto modificado a la lista de resultados
				#w_path = str(self.reports_path) + "/geoloc.json"
				w_path = os.path.join(self.reports_path, "georeport.json")
				#print(w_path)
				with open(w_path, 'w') as f:
					for obj in result:
						f.write(json.dumps(obj) + '\n')  # Escribir cada objeto en el archivo de salida, separado por 					
			#except (UnicodeError, TypeError, IOError) as e:
			#	raise CuckooReportError("Geolookup Report Failed: %s" % e)
        
