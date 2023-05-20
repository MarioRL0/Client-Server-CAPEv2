import json
import requests
import os

def analysis_vt(file_path):
	'''
	Obtiene respuesta de VT usando su API.
	@param file_path: ruta del archivo a analizar
	@return: cadena de valoracion del analisis
	'''  
	api_key = "6d098150c326624dab93227dccb013dab875c135027400b076216b8f1734ecd4"
	# Para cuando use una variable de entorno
	# API_KEY = os.environ['VT_API']
	files = {"file": open(file_path, "rb")}
	headers = {"x-apikey": api_key}
	# API request para obtener ID del analisis
	if os.path.getsize(file_path) > 32000000:
		print("Mayor que 32 MB")
		url = "https://www.virustotal.com/api/v3/files/upload_url"
		response = requests.get(url, headers=headers)
		upload_url = response.json()["data"]
		print("##################################################################################################")
		print(response)
	else:
		print("Menor que 32 MB")
		upload_url = "https://www.virustotal.com/api/v3/files"

	response = requests.post(upload_url, files=files, headers=headers)
	print("##################################################################################################")
	print(response)
	# API respond
	response_json = response.json()
	# Obtiene del respond el analisis ID
	analysis_id = response_json["data"]["id"]

	# Obtiene el analisis a partir del ID
	url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
	headers = {"x-apikey": api_key}
	# API request
	response = requests.get(url, headers=headers)
	# API respond
	print("##################################################################################################")
	print(response)
	response_json = response.json()

	if response_json ["data"]["attributes"]["stats"]["malicious"] == 0:
		return "El archivo no es malicioso"
		if response_json ["data"]["attributes"]["stats"]["suspicious"] == 0:
			return "El archivo no es sospechoso"
		else:
			return "El archivo es sospechoso"
	else:
		return "El archivo es malicioso"


