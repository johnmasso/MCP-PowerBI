# -*- coding: utf-8 -*-
"""
API para el Asistente de Análisis de Power BI (MCP) v2.0
"""
from flask import Flask, request, jsonify
import mcp  # Importa nuestro script refactorizado
from pbixray import PBIXRay

app = Flask(__name__)

# --- Funciones de Utilidad de la API ---

def process_analysis_request():
    """Procesa una petición entrante, carga el modelo y maneja errores."""
    data = request.get_json()
    if not data or 'file_path' not in data:
        return None, (jsonify({"error": "Falta el parámetro 'file_path' en el cuerpo de la petición."}), 400)
    
    file_path = data['file_path']
    try:
        model = PBIXRay(file_path)
        return model, None
    except FileNotFoundError:
        return None, (jsonify({"error": f"Archivo no encontrado en la ruta: {file_path}"}), 404)
    except Exception as e:
        return None, (jsonify({"error": f"Ha ocurrido un error inesperado: {str(e)}"}), 500)

# --- Endpoints de la API ---

@app.route('/')
def index():
    """Endpoint de bienvenida para verificar que la API está funcionando."""
    return "¡La API del Asistente de Power BI (MCP) v2.0 está en funcionamiento!"

@app.route('/analyze/tables', methods=['POST'])
def tables_api():
    """Devuelve las tablas del modelo."""
    model, error = process_analysis_request()
    if error: return error
    return jsonify({"tables": mcp.get_tables(model)})

@app.route('/analyze/dax_measures', methods=['POST'])
def dax_measures_api():
    """Devuelve las medidas DAX del modelo."""
    model, error = process_analysis_request()
    if error: return error
    return jsonify({"dax_measures": mcp.get_dax_measures(model)})

@app.route('/analyze/relationships', methods=['POST'])
def relationships_api():
    """Devuelve las relaciones del modelo."""
    model, error = process_analysis_request()
    if error: return error
    return jsonify({"relationships": mcp.get_relationships(model)})

@app.route('/analyze/power_query', methods=['POST'])
def power_query_api():
    """Devuelve las consultas de Power Query."""
    model, error = process_analysis_request()
    if error: return error
    return jsonify({"power_queries": mcp.get_power_query(model)})

@app.route('/analyze/best_practices_dax', methods=['POST'])
def best_practices_dax_api():
    """Devuelve una lista de recomendaciones de buenas prácticas para DAX."""
    model, error = process_analysis_request()
    if error: return error
    return jsonify({"dax_best_practices_findings": mcp.analyze_dax_best_practices(model)})

@app.route('/analyze/best_practices_power_query', methods=['POST'])
def best_practices_power_query_api():
    """Devuelve una lista de recomendaciones de buenas prácticas para Power Query."""
    model, error = process_analysis_request()
    if error: return error
    return jsonify({"power_query_best_practices_findings": mcp.analyze_power_query_best_practices(model)})


if __name__ == '__main__':
    app.run(debug=True)
