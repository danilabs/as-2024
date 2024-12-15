#!/bin/bash

# Variables
DOCKER_IMAGE_NAME="flask-api"
NGINX_SITE_PATH="/etc/nginx/sites-available/flask_api"
NGINX_SITE_ENABLED_PATH="/etc/nginx/sites-enabled/flask_api"

# 1. Instalar Docker (si no está instalado)
echo "Instalando Docker..."
sudo apt update
sudo apt install -y docker.io

# 2. Construir la imagen Docker para la API
echo "Construyendo la imagen Docker para la API..."
sudo docker build -t $DOCKER_IMAGE_NAME .

# 3. Ejecutar el contenedor Docker
echo "Ejecutando el contenedor Docker para la API..."
sudo docker run -d -p 5000:5000 --name flask-api $DOCKER_IMAGE_NAME

# 4. Instalar Nginx (si no está instalado)
echo "Instalando Nginx..."
sudo apt install -y nginx

# 5. Configurar Nginx para redirigir a la API Flask
echo "Configurando Nginx..."
cat > "$NGINX_SITE_PATH" <<EOL
server {
    listen 80;
    server_name $(hostname -I | awk '{print $1}');

    location / {
        proxy_pass http://127.0.0.1:5000;  # Redirige al puerto donde Flask está escuchando
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

# 6. Habilitar el sitio de Nginx y reiniciar el servicio
echo "Habilitando el sitio de Nginx..."
sudo ln -s "$NGINX_SITE_PATH" "$NGINX_SITE_ENABLED_PATH"
sudo systemctl restart nginx

# 7. Confirmar que todo está funcionando
echo "La API Flask debería estar ahora disponible a través de Nginx."
echo "Puedes acceder a ella en http://$(hostname -I | awk '{print $1}')/"
echo "Prueba las siguientes rutas:"
echo "  /user/test"
echo "  /user/dev"
echo "  /user/admin"
