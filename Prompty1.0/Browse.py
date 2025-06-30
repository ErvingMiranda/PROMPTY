import os
from tkinter import Tk, filedialog

def abrir_archivo():
    archivo = filedialog.askopenfilename(title="Selecciona un archivo para abrir")
    
    if archivo:
        try:
            os.startfile(archivo)
            print(f"Abriendo: {archivo}")
        except Exception as e:
            print(f"Error al abrir el archivo: {e}")
    else:
        print("No se seleccionó ningún archivo.")

abrir_archivo()