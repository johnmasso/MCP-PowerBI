# -*- coding: utf-8 -*-
"""
API para el Asistente de Análisis de Power BI (MCP) v2.0
Permite la carga y análisis de archivos .pbix.
"""
import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import mcp  # Nuestro script de lógica
from pbixray import PBIXRay

# --- Configuración de la App ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pbix'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Funciones de Utilidad de la API ---

def allowed_file(filename):
    """Verifica si la extensión del archivo es permitida."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Endpoints de la API ---

@app.route('/')
def index():
    """Endpoint de bienvenida para verificar que la API está funcionando."""
    return "¡La API del Asistente de Power BI (MCP) v2.0 está en funcionamiento!"

@app.route('/upload_and_analyze', methods=['POST'])
def upload_and_analyze_api():
    """Recibe un archivo .pbix, lo analiza por completo y devuelve los resultados."""
    if 'file' not in request.files:
        return jsonify({"error": "No se encontró el archivo en la petición."}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No se seleccionó ningún archivo."}), 400

    if file and allowed_file(file.filename):
        # Asegurarse de que el directorio de subida exista
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            # Cargar el modelo y ejecutar todos los análisis
            model = PBIXRay(file_path)
            
            results = {
                "filename": filename,
                "analysis": {
                    "tables": mcp.get_tables(model),
                    "dax_measures": mcp.get_dax_measures(model),
                    "relationships": mcp.get_relationships(model),
                    "power_queries": mcp.get_power_query(model),
                    "dax_best_practices_findings": mcp.analyze_dax_best_practices(model),
                    "power_query_best_practices_findings": mcp.analyze_power_query_best_practices(model)
                }
            }
            
            # Limpiar el archivo subido después del análisis
            os.remove(file_path)
            
            return jsonify(results)

        except Exception as e:
            # Limpiar el archivo subido incluso si hay un error
            if os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({"error": "Ocurrió un error durante el análisis: {str(e)}"}), 500
    
    return jsonify({"error": "Tipo de archivo no permitido."}), 400

if __name__ == '__main__':
    app.run(debug=True)