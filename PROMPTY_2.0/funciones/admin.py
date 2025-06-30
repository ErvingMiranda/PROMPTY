import os
import sys
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

# Asegura acceso a la carpeta raíz del proyecto para importar helpers
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utilidades.helpers import capitalizar_dato, limpiar_pantalla

def modo_admin():
    limpiar_pantalla()
    print(f"\n{Fore.MAGENTA}🔐 Bienvenido al modo administrador de datos curiosos.{Style.RESET_ALL}")

    archivo = os.path.join(BASE_DIR, "datos", "datos_curiosos.txt")

    while True:
        modo = input(f"\n{Fore.CYAN}¿Deseas agregar (a) o sobrescribir (s) los datos?{Style.RESET_ALL} ").lower()
        if modo in ['a', 's']:
            break
        else:
            print(f"{Fore.RED}❌ Opción no válida. Escribe 'a' para agregar o 's' para sobrescribir.{Style.RESET_ALL}")

    while True:
        try:
            cantidad = int(input(f"\n{Fore.CYAN}¿Cuántos datos curiosos deseas ingresar?{Style.RESET_ALL} "))
            if cantidad > 0:
                break
            else:
                print(f"{Fore.RED}❌ Debe ser un número mayor a cero.{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}❌ Por favor, introduce un número válido.{Style.RESET_ALL}")

    datos_nuevos = []
    for i in range(cantidad):
        while True:
            dato = input(f"\n{Fore.YELLOW}Ingrese el dato curioso #{i+1}:{Style.RESET_ALL} ").strip()
            if not dato:
                print(f"{Fore.RED}❌ El dato no puede estar vacío.{Style.RESET_ALL}")
                continue

            dato_cap = capitalizar_dato(dato)
            confirmar = input(f"{Fore.CYAN}¿Está correcto este dato?{Style.RESET_ALL} \"{dato_cap}\" (s/n): ").lower()
            if confirmar == 's':
                datos_nuevos.append(dato_cap)
                break
            else:
                print(f"{Fore.YELLOW}🔁 Volvamos a intentarlo.{Style.RESET_ALL}")

    modo_apertura = 'a' if modo == 'a' else 'w'
    with open(archivo, modo_apertura) as f:
        for dato in datos_nuevos:
            f.write(dato + "\n")

    print(f"\n{Fore.GREEN}✅ Datos guardados correctamente.{Style.RESET_ALL}")
    print(f"\n{Fore.BLUE}📖 Datos curiosos registrados:{Style.RESET_ALL}")
    with open(archivo, 'r') as f:
        for idx, linea in enumerate(f.readlines(), start=1):
            print(f"{Fore.CYAN}{idx}.{Style.RESET_ALL} {linea.strip()}")

    return f"\n{Fore.GREEN}✅ Modo administrador completado.{Style.RESET_ALL}"