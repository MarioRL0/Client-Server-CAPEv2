import tkinter as tk
from tkinter import messagebox
import os
from funciones import *

def validar_formato(directorio, cape_conn):
	'''
	Valida el formato de los datos de entrada
	@param directorio: directorio a monitorizar
	@param cape_conn: datos de conexion con CAPE IP:PORT
	@return: Dependiendo de la validez de los parametros devuelve mensaje de error o no
	'''
	# Valida formato de directorio
	if not os.path.isdir(directorio):
		return False, "Directorio no valido"
	# Valida formato IP:PORT
	cape_conn = cape_conn.split(":")
	# Comprueba que solo tenga 2 elementos
	if len(cape_conn) != 2:
		return False, "No se respeta el formato IP:PORT"
	ip, port = cape_conn
	# Comprueba que la IP la formen 4 octetos entre 1 y 254, ya que tienen que ser IPs validas
	octets = ip.split(".")
	if len(octets) != 4:
		return False, "IP no valida, se necesitan 4 octetos"
	for octet in octets:
		if not octet.isdigit() or not 0 < int(octet) < 255:
		    return False, "IP no valida, octetos no cumplen rangos validos de IP"
	# Verifica que el puerto sea un numero >1024, para que no corresponda con valores reservados
	if not port.isdigit():
		return False, "El puerto introducido no es un digito"
	if int(port) <= 1024:
		return False, "El puerto introducido esta reservado"

	return True, "OK"
    
def aceptar(directorio_entry,sanbox_ip_entry,ventana):
	'''
	Llama a la funcion monitor_dir() con los datos introducidos, si son validos
	@param directorio_entry: directorio a monitorizar
	@param sanbox_ip_entry: datos de conexion con CAPE IP:PORT
	@param ventana: Ventana a cerrar
	'''
	directorio = str(directorio_entry.get())
	cape_conn = str(sanbox_ip_entry.get())
	valido, error_msg = validar_formato(directorio, cape_conn)
	if not valido:
		messagebox.showerror("Error", error_msg)
		return
	cape_ip = str(cape_conn.split(":")[0])
	cape_port = int(cape_conn.split(":")[1])
	ventana.destroy()
	monitor_dir(directorio,cape_ip,cape_port)

def ventana():
	'''
	Interfaz grafica para usuario
	'''    
	ventana = tk.Tk()
	ventana.title("Monitorización")

	directorio_label = tk.Label(ventana, text="Directorio a monitorizar:")
	directorio_label.pack()

	directorio_entry = tk.Entry(ventana)
	directorio_entry.pack()

	sanbox_ip_label = tk.Label(ventana, text="CAPE IP:PORT ")
	sanbox_ip_label.pack()

	sanbox_ip_entry = tk.Entry(ventana)
	sanbox_ip_entry.pack()

	aceptar_button = tk.Button(
		ventana,
		text="Aceptar", 
		command=lambda: aceptar(directorio_entry,sanbox_ip_entry,ventana)
		)

	aceptar_button.pack()

	ventana.mainloop()
