import requests
# Envía el archivo a la API de CAPEv2 para su análisis
with open('/home/xxx/Downloads/vlc-3.0.18-win32.exe', 'rb') as f:
    text = f.read()
url = 'https://192.168.153.5/analysis/api/v2/submit'
params = {'apikey': ''}
files = {'file': ('vlc-3.0.18-win32.exe', text)}
response = requests.post(url, params=params, files=files)

# Imprime la respuesta de la API
print(response.json())
