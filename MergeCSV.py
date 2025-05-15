import pandas as pd
import os
import numpy as np
import re
import matplotlib.pyplot as plt

# Lista de archivos CSV a combinar
carpeta = r'C:\Users\mmartic\Desktop\test'  # Cambia esta ruta

def LTIME_to_seconds(LTIME):
    
    conversor = {"h": 3600,
                 "m": 60,
                 "s": 1,
                 "ms": 1e-3,
                 "us": 1e-6,
                 "ns": 1e-9}

    units = re.split(r'\d+', LTIME)[1:]
    numbers_str = re.findall(r'\d+', LTIME)
    numbers = [int(number) for number in numbers_str]
    
    total_time = 0

    for number, unit in zip(numbers, units):
        total_time += number * conversor[unit]
    
    return total_time

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

time_array = np.empty((df.shape[0],))

for index, row in df.iterrows():
        time_array[index] = LTIME_to_seconds(row["Time(s)"])
        
time_array -= time_array[0]

y1 = df['MC SW Overview - Actual Position(mm)'].values
y2 = df['MC SW Force Control - Measured Force(N)'].values
y3 = df['MC SW Force Control - Target Force(N)'].values

# Crear figura y primer eje (Y1 - izquierda)
fig, ax1 = plt.subplots(figsize=(8, 5))
ax1.plot(time_array, y1, 'r-', label='Actual Position(mm)')
ax1.set_ylabel('Actual Position(mm)', color='r')
ax1.tick_params(axis='y', labelcolor='r')

# Segundo eje (Y2 - derecha)
ax2 = ax1.twinx()
ax2.plot(time_array, y2, 'b', label='Measured Force(N)')
ax2.set_ylabel('Measured Force(N)', color='b')
ax2.tick_params(axis='y', labelcolor='b')

# Tercer eje (Y3 - también derecha, pero desplazado)
ax3 = ax1.twinx()
ax3.spines["right"].set_position(("outward", 60))  # Desplazar eje 60 px a la derecha
ax3.plot(time_array, y3, 'g', label='Target Force(N)')
ax3.set_ylabel('Target Force(N)', color='g')
ax3.tick_params(axis='y', labelcolor='g')

# Opcional: ocultar marco duplicado del eje
ax3.spines["right"].set_visible(True)

# Eje X compartido
ax1.set_xlabel('Time(s)')

# Título
plt.title("LinMot data")
plt.tight_layout()
plt.show()