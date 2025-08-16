# -*- coding: utf-8 -*-
"""MCP (Metacali Control Program) v1.0 - Asistente de Análisis de Power BI."""

import sys
import tkinter as tk
from tkinter import filedialog
from pbixray import PBIXRay

# --- Funciones de Utilidad ---

def select_pbix_file():
    """Abre una ventana para que el usuario seleccione un archivo .pbix."""
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de tkinter
    file_path = filedialog.askopenfilename(
        title="Selecciona un archivo Power BI",
        filetypes=(("Power BI files", "*.pbix"), ("All files", "*.*"))
    )
    return file_path

def get_model_schema(model):
    """Construye un string legible con el esquema de tablas y columnas del modelo."""
    try:
        schema = ""
        all_columns = model.schema
        if all_columns is not None and not all_columns.empty:
            for table_name, columns in all_columns.groupby('TableName'):
                schema += f"Tabla: '{table_name}'\n"
                for column in columns.itertuples():
                    schema += f"  - Columna: '{column.ColumnName}'\n"
                schema += "\n"
            return schema
        else:
            return "No se pudo leer el esquema de columnas del modelo."
    except AttributeError:
        return "Error: No se pudo obtener el atributo 'schema' del modelo."

# --- Funciones de Inspección (Refactorizadas para devolver datos) ---

def get_tables(model):
    """Devuelve una lista con los nombres de las tablas del modelo."""
    try:
        tables = model.tables
        return tables.tolist() if tables.any() else []
    except AttributeError:
        return ["Error: No se pudo obtener el atributo 'tables' del modelo."]

def get_dax_measures(model):
    """Devuelve un listado de diccionarios con las medidas DAX."""
    try:
        dax_measures = model.dax_measures
        if dax_measures is not None and not dax_measures.empty:
            return dax_measures.to_dict(orient='records')
        return []
    except AttributeError:
        return [{"error": "No se pudo obtener el atributo 'dax_measures' del modelo."}]

def get_relationships(model):
    """Devuelve un listado de diccionarios con las relaciones del modelo."""
    try:
        relationships = model.relationships
        if relationships is not None and not relationships.empty:
            return relationships.to_dict(orient='records')
        return []
    except AttributeError:
        return [{"error": "No se pudo obtener el atributo 'relationships' del modelo."}]

def get_power_query(model):
    """Devuelve un listado de diccionarios con las consultas de Power Query."""
    try:
        power_queries = model.power_query
        if power_queries is not None and not power_queries.empty:
            return power_queries.reset_index().to_dict(orient='records')
        return []
    except AttributeError:
        return [{"error": "No se pudo obtener el atributo 'power_query' del modelo."}]

# --- Funciones de Optimización y Generación ---

def analyze_dax_best_practices(model):
    """Analiza y devuelve una lista de hallazgos sobre buenas prácticas en DAX."""
    findings = []
    try:
        dax_measures = model.dax_measures
        if dax_measures is not None and not dax_measures.empty:
            for measure in dax_measures.itertuples():
                expression = measure.Expression or ''
                if " IN {" in expression and expression.count(',') > 3:
                    finding = (f"[OPORTUNIDAD] En la medida: \"{measure.Name}\". "
                               "Se recomienda mover la lógica de la lista 'IN' a una columna calculada.")
                    findings.append(finding)
        return findings
    except AttributeError:
        return ["Error: No se pudo obtener el atributo 'dax_measures' del modelo."]

def analyze_power_query_best_practices(model):
    """Analiza y devuelve una lista de hallazgos sobre buenas prácticas en Power Query."""
    findings = []
    try:
        power_queries = model.power_query
        if power_queries is not None and not power_queries.empty:
            for name, row in power_queries.iterrows():
                expression = row.Expression or ''
                if "File.Contents" in expression or "Folder.Files" in expression:
                    try:
                        start = expression.find('("') + 2
                        end = expression.find('"', start)
                        path = expression[start:end]
                        if ':\\' in path:
                            finding = (f"[OPORTUNIDAD] En la consulta: \"{name}\". "
                                       f"La consulta usa una ruta de archivo local: {path}. "
                                       "Se recomienda usar una fuente de datos centralizada.")
                            findings.append(finding)
                    except:
                        continue
        return findings
    except AttributeError:
        return ["Error: No se pudo obtener el atributo 'power_query' del modelo."]

def generar_medida_dax(model):
    """Imprime el contexto necesario para que la IA genere una medida DAX."""
    print("\n--- Generador de Medidas DAX con IA ---")
    schema = get_model_schema(model)
    print("Por favor, describe la medida DAX que necesitas crear.")
    user_request = input("Ejemplo: 'Suma de Siniestros donde la severidad es Alta'\n> ")
    print("\n" + "="*50)
    print("Copia el siguiente contexto y pégalo en la consola de Gemini:")
    print("--- INICIO CONTEXTO PARA IA ---")
    print("**Tarea:** Generar una medida DAX.")
    print(f"**Petición Usuario:** {user_request}")
    print("**Esquema del Modelo:**")
    print(schema)
    print("--- FIN CONTEXTO PARA IA ---")
    print("="*50 + "\n")

def generar_columna_calculada(model):
    """Imprime el contexto necesario para que la IA genere una columna calculada DAX."""
    print("\n--- Generador de Columnas Calculadas con IA ---")
    tables = get_tables(model)
    if not tables:
        print("No se encontraron tablas en el modelo.")
        return
    print("Tablas disponibles en el modelo:")
    for i, table in enumerate(tables):
        print(f"{i + 1}. {table}")
    try:
        table_choice_num = int(input("Selecciona el número de la tabla donde quieres añadir la columna: "))
        if not 1 <= table_choice_num <= len(tables):
            print("Selección inválida.")
            return
        target_table = tables[table_choice_num - 1]
    except (ValueError, IndexError):
        print("Entrada no válida.")
        return
    schema = get_model_schema(model)
    print(f"\nDescribe la columna calculada que necesitas crear en la tabla '{target_table}'.")
    user_request = input("Ejemplo: 'Una columna que una el Nombre y el Apellido'\n> ")
    print("\n" + "="*50)
    print("Copia el siguiente contexto y pégalo en la consola de Gemini:")
    print("--- INICIO CONTEXTO PARA IA ---")
    print("**Tarea:** Generar una columna calculada DAX.")
    print(f"**Tabla Objetivo:** {target_table}")
    print(f"**Petición Usuario:** {user_request}")
    print("**Esquema del Modelo:**")
    print(schema)
    print("--- FIN CONTEXTO PARA IA ---")
    print("="*50 + "\n")

# --- Menú y Lógica Principal (Modo Interactivo) ---

def display_menu():
    """Muestra el menú de opciones al usuario."""
    print("\n" + "="*30)
    print("MCP - Asistente de Power BI")
    print("="*30)
    print("--- Inspeccionar ---")
    print("1. Ver Tablas del Modelo")
    print("2. Ver Medidas DAX")
    print("3. Ver Relaciones")
    print("4. Ver Consultas Power Query (M)")
    print("--- Optimizar y Generar ---")
    print("5. Analizar Buenas Prácticas DAX")
    print("6. Analizar Buenas Prácticas Power Query")
    print("g. Generar Medida DAX con IA")
    print("c. Generar Columna Calculada con IA")
    print("--- General ---")
    print("a. Analizar Todo")
    print("s. Salir")
    print("="*30)

def main():
    """Función principal que orquesta el análisis del archivo PBIX."""
    pbix_file_path = select_pbix_file()
    if not pbix_file_path:
        print("No se seleccionó ningún archivo. Saliendo del programa.")
        return

    print(f"Cargando el archivo: {pbix_file_path}...")
    try:
        model = PBIXRay(pbix_file_path)
        print("¡Archivo cargado con éxito!")
    except Exception as e:
        print(f"Ocurrió un error inesperado al cargar el archivo: {e}")
        return

    while True:
        display_menu()
        try:
            choice = input("Selecciona una opción: ").lower()
            if choice == '1':
                tables = get_tables(model)
                print("\n--- Tablas del Modelo ---")
                for table in tables:
                    print(f"- {table}")
            elif choice == '2':
                measures = get_dax_measures(model)
                print("\n--- Medidas DAX ---")
                for measure in measures:
                    print(f"- Nombre: {measure['Name']}\n  Expresión: {measure['Expression']}\n")
            elif choice == '3':
                relationships = get_relationships(model)
                print("\n--- Relaciones del Modelo ---")
                for rel in relationships:
                    print(f"- De: {rel['FromTableName']} ({rel['FromColumnName']})\n  A:  {rel['ToTableName']} ({rel['ToColumnName']})\n  Activa: {rel['IsActive']}\n")
            elif choice == '4':
                queries = get_power_query(model)
                print("\n--- Código Power Query (M) ---")
                for query in queries:
                    print(f"- Nombre: {query['Name']}\n  Código M:\n{query['Expression']}\n")
            elif choice == '5':
                print("\n--- Análisis de Buenas Prácticas DAX ---")
                findings = analyze_dax_best_practices(model)
                if findings:
                    for finding in findings:
                        print(f"- {finding}")
                else:
                    print("¡Buen trabajo! No se encontraron problemas comunes.")
            elif choice == '6':
                print("\n--- Análisis de Buenas Prácticas Power Query ---")
                findings = analyze_power_query_best_practices(model)
                if findings:
                    for finding in findings:
                        print(f"- {finding}")
                else:
                    print("¡Buen trabajo! No se encontraron problemas comunes.")
            elif choice == 'g':
                generar_medida_dax(model)
            elif choice == 'c':
                generar_columna_calculada(model)
            elif choice == 'a':
                # Analizar todo
                tables = get_tables(model)
                print("\n--- Tablas del Modelo ---")
                for table in tables:
                    print(f"- {table}")
                measures = get_dax_measures(model)
                print("\n--- Medidas DAX ---")
                for measure in measures:
                    print(f"- Nombre: {measure['Name']}\n  Expresión: {measure['Expression']}\n")
                # ... y así para las demás funciones de análisis ...
            elif choice == 's':
                print("Saliendo del programa.")
                break
            else:
                print("Opción no válida. Por favor, intenta de nuevo.")
        except KeyboardInterrupt:
            print("\n\nSaliendo del programa.")
            break
        except Exception as e:
            print(f"\nOcurrió un error durante la ejecución: {e}")

if __name__ == "__main__":
    main()