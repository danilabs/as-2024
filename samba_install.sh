#!/bin/bash

# Nombre de la carpeta y directorio donde se creará
FOLDER_NAME="logs"
DIRECTORY="/mnt/smb/$FOLDER_NAME"

# Crear la carpeta
echo "Creando la carpeta $DIRECTORY..."
mkdir -p "$DIRECTORY"

# Asignar permisos 777 para que sea accesible por todos
echo "Asignando permisos 777 a la carpeta..."
chmod 777 "$DIRECTORY"

# Instalar Samba si no está instalado
echo "Instalando Samba..."
sudo apt update
sudo apt install -y samba

# Configurar la carpeta compartida en Samba
echo "Configurando Samba para compartir la carpeta..."

# Agregar la configuración de la carpeta compartida a smb.conf
echo "[Logs]" | sudo tee -a /etc/samba/smb.conf > /dev/null
echo "path = $DIRECTORY" | sudo tee -a /etc/samba/smb.conf > /dev/null
echo "browseable = yes" | sudo tee -a /etc/samba/smb.conf > /dev/null
echo "read only = no" | sudo tee -a /etc/samba/smb.conf > /dev/null
echo "guest ok = yes" | sudo tee -a /etc/samba/smb.conf > /dev/null

# Configurar seguridad para permitir acceso sin autenticación
echo "security = share" | sudo tee -a /etc/samba/smb.conf > /dev/null

# Reiniciar el servicio de Samba para aplicar cambios
echo "Reiniciando el servicio Samba..."
sudo systemctl restart smbd

# Confirmación
echo "La carpeta '$FOLDER_NAME' está ahora compartida y accesible sin autenticación."
echo "Puede acceder a ella desde cualquier equipo de la red utilizando:"
echo "smb://$(hostname -I | awk '{print $1}')/$FOLDER_NAME"

