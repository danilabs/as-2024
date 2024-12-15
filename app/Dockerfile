# Usar una imagen base de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos necesarios
COPY requirements.txt /app/
COPY app.py /app/

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto en el que la aplicación Flask estará escuchando
EXPOSE 5000

# Ejecutar la aplicación Flask
CMD ["python", "app.py"]
