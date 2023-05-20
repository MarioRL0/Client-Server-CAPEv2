import argparse
from modo_usuario import ventana
from modo_auto import run_auto

def automatico(args):	
	'''
	Modo automatico (por terminal).
	@param args: argumentos de entrada
	''' 
	run_auto(str(args.dir),str(args.conf))

def usuario():	
	'''
	Modo usuario, lanza ventana para introducir parametros
	''' 
	ventana()

def main():
	'''
	Define los argumentos de entrada
	'''
	parser = argparse.ArgumentParser(description="Descripción de la aplicación")
	parser.add_argument("-m", "--modo", required=True, choices=["auto", "user"], help="Modo de la aplicación: auto o user")
	parser.add_argument("-c", "--conf", nargs='?', required='auto' in argparse._sys.argv, help="Archivo de configuración para el modo automático")
	parser.add_argument("-d", "--dir", nargs='?', required='auto' in argparse._sys.argv, help="Ruta del directorio a monitorizar")
	# Parsea los argumentos de entrada
	args = parser.parse_args()
	# Selecciona modo
	if args.modo == "auto":
		  automatico(args)
	elif args.modo == "user":
		  usuario()

if __name__ == "__main__":
	main()

