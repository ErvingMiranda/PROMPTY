def capitalizar_dato(texto):
    return texto.capitalize()

def administrar_datos_curiosos():
    print("\n🔐 Bienvenido al modo administrador de datos curiosos.")

    archivo = "datos_curiosos.txt"

    while True:
        modo = input("\n¿Deseas agregar (a) o sobrescribir (s) los datos?: ").lower()
        if modo in ['a', 's']:
            break
        else:
            print("Opción no válida. Escribe 'a' para agregar o 's' para sobrescribir.")

    while True:
        try:
            cantidad = int(input("¿Cuántos datos curiosos deseas ingresar?: "))
            if cantidad > 0:
                break
            else:
                print("Debe ser un número mayor a cero.")
        except ValueError:
            print("Por favor, introduce un número válido.")

    datos_nuevos = []
    for i in range(cantidad):
        while True:
            dato = input(f"Ingrese el dato curioso #{i+1}: ").strip()
            if not dato:
                print("❌ El dato no puede estar vacío.")
                continue

            dato_cap = capitalizar_dato(dato)
            confirmar = input(f"¿Está correcto este dato? \"{dato_cap}\" (s/n): ").lower()
            if confirmar == 's':
                datos_nuevos.append(dato_cap)
                break
            else:
                print("🔁 Volvamos a intentarlo.")
                
    # Escribir en el archivo
    modo_apertura = 'a' if modo == 'a' else 'w'
    with open(archivo, modo_apertura, encoding='utf-8') as f:
        for dato in datos_nuevos:
            f.write(dato + "\n")

    print("\n✅ Datos guardados correctamente.")

    # Mostrar contenido actual del archivo
    print("\n📖 Datos curiosos registrados:")
    with open(archivo, 'r', encoding='utf-8') as f:
        for idx, linea in enumerate(f.readlines(), start=1):
            print(f"{idx}. {linea.strip()}")

if __name__ == "__main__":
    administrar_datos_curiosos()