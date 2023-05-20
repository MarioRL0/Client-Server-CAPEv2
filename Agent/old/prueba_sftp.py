import pysftp 

def transmision_sftp(archivo,host,_port,user,_password):

	with pysftp.Connection(host, port=_port, username=user, password=_password) as sftp:
		with sftp.cd("."):
			sftp.put(archivo)
			print("[*] Archivo enviado")
	
	
transmision_sftp("/home/xxx/Desktop/Scripts_auto/transferir_imagen.jpeg","192.168.153.5",22,"xxx","pass")
#transmision_sftp("/home/xxx/Downloads/vlc-3.0.18-win32.exe","192.168.153.5","22022","anonymous","")
