# Flask API con Docker y Nginx

Este proyecto crea una API sencilla en Flask que tiene tres tipos de usuario: `test`, `dev` y `admin`. La API está contenida en un contenedor Docker y se expone a través de un servidor Nginx.

## Estructura del Proyecto

El proyecto contiene los siguientes archivos:

- `app.py`: Código de la API en Flask.
- `Dockerfile`: Instrucciones para construir la imagen de Docker para la API.
- `nginx.conf`: Configuración de Nginx para redirigir las solicitudes a la API Flask.
- `setup.sh`: Script para automatizar la instalación y configuración.
- `requirements.txt`: Dependencias necesarias para ejecutar la API Flask.

## Requisitos

Antes de comenzar, asegúrate de tener los siguientes requisitos instalados:

- Docker
- Nginx

## Instalación y Configuración

1. **Clona el repositorio**:

    ```bash
    git clone https://github.com/tu_usuario/tu_repositorio.git
    cd tu_repositorio
    ```

2. **Haz el script `setup.sh` ejecutable**:

    ```bash
    chmod +x setup.sh
    ```

3. **Ejecuta el script de instalación**:

    ```bash
    ./setup.sh
    ```

   Este script automatiza la instalación de Docker y Nginx, construye la imagen de Docker para la API y configura Nginx para redirigir las solicitudes a la API Flask.

## Rutas de la API

Una vez que la API esté corriendo, puedes probar las siguientes rutas:

- **`/user/test`**: Acceso para usuarios tipo `test`.
- **`/user/dev`**: Acceso para usuarios tipo `dev`.
- **`/user/admin`**: Acceso para usuarios tipo `admin`.

## Ver la API en Acción

Después de ejecutar el script, la API estará disponible a través de Nginx en la dirección IP de tu servidor. Puedes acceder a la API usando un navegador web o herramientas como `curl`.

```bash
curl http://<tu-ip>
