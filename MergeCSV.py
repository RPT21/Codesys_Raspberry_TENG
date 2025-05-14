import pandas as pd
import os

# Lista de archivos CSV a combinar
carpeta = r'S:\TriboMedData\CharacterizationData\TENGData\Test_grabacion_motor'  # Cambia esta ruta

def sort_function(string):
    return int(string.split("_")[-1].split(".")[0])

archivos = [f for f in os.listdir(carpeta) if f.endswith('.csv')]
archivos.sort(key=sort_function)

# Crear un dataframe vacío
df_combinado = pd.DataFrame()

# Iterar sobre cada archivo CSV
for archivo in archivos:
    # Leer el CSV
    df = pd.read_csv(os.path.join(carpeta, archivo), sep=';')
    
    # Concatenar el archivo al dataframe combinado
    df_combinado = pd.concat([df_combinado, df], ignore_index=True)

# Guardar el dataframe combinado en un nuevo archivo CSV
df_combinado.to_csv('archivo_combinado.csv', index=False)

print("Archivos combinados correctamente!")

