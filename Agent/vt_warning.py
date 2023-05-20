import tkinter as tk

def yes_action(ans,ventana):
	'''
	Pone a 1 el elemento go, para indicar que se mande a CAPE el fichero
	@param ans: diccionario para modificar 'go'
	@param ventana: ventana con la que debe interactuar
	'''
	ans["go"] = 1
	ventana.destroy()

def no_action(ans,ventana):
	'''
	Pone a 0 el elemento go, para indicar que no se mande a CAPE el fichero
	@param ans: diccionario para modificar 'go'
	@param ventana: ventana con la que debe interactuar
	'''   
	ans["go"] = 0
	ventana.destroy()

def vt_window(vt_msg):
	'''
	Crea ventana con un mensaje que corresponde con el resultado de VT
	@param vt_msg: resultado de VT
	''' 
	ventana = tk.Tk()
	ventana.title("Aviso VirusTotal")
	ventana.geometry("400x100")
	window_msg = vt_msg + " ¿Desea analizarlo en el sandbox?"
	mensaje = tk.Label(ventana, text=window_msg)
	mensaje.pack(pady=10)
	# Es un diccionario, para actualizar el valor al pulsar el boton
	ans = {"go" : 0}
	boton_si = tk.Button(ventana, text="Si", command=lambda: yes_action(ans,ventana))
	boton_si.pack(side=tk.LEFT, padx=10)
	boton_no = tk.Button(ventana, text="No", command=lambda: no_action(ans,ventana))
	boton_no.pack(side=tk.RIGHT, padx=10)
	ventana.mainloop()
	return ans["go"]
