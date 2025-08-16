# Usar una imagen oficial de Python como base
FROM python:3.11-slim

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar el archivo de requerimientos e instalar las dependencias
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos de la aplicación al directorio de trabajo
# (api.py, mcp.py, etc.)
COPY . .

# Exponer el puerto en el que Flask se ejecutará
EXPOSE 5000

# Comando para ejecutar la aplicación cuando el contenedor se inicie
# Usamos gunicorn para un servidor de producción más robusto
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "api:app"]
