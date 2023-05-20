#!/bin/bash

# Se comprueba si se ha pasado un argumento (el nombre del archivo)
if [ $# -eq 0 ]; then
  echo "Se debe proporcionar el nombre del archivo como argumento"
  exit 1
fi

# Se define la ubicación de origen y la ubicación de destino
src="/home/xxx/$1"
dst="/home/cape/$1"
#dst_zip="/root/servidor_auto/files/$2"
# Se comprueba si el archivo existe en la ubicación de origen
if [ ! -f "$src" ]; then
  echo "El archivo $1 no existe en la ubicación de origen"
  exit 1
fi

# Se mueve el archivo a la ubicación de destino
sudo mv "$src" "$dst"

# Para ejecutarlo con submit el propietario debe ser root
sudo chown root:root "$dst"
sudo chmod g-w "$dst"

sudo bash submit_cape.sh $dst
#################################################################################
# Se encapsula con password el archivo para unificar el formato de subida a CAPE

#pass="standard_pass"

#cd /root/servidor_auto/files/
#zip -P $pass $2 $1

#rm "$dst"
#################################################################################
# Se sale del script
exit 0
