# PROMPTY

PROMPTY es un asistente por voz escrito en Python. Este repositorio contiene distintas versiones que muestran la evolución del proyecto.

## Ejecución rápida

Cada versión cuenta con su propio archivo principal:

- **Prompty1.0**: scripts iniciales ubicados en `Prompty1.0`. Ejecuta por ejemplo `python Prompty1.0.py` o `Prompty1.2.py` según el script que quieras probar.
- **PROMPTY_2.0**: versión modularizada. Corre `python PROMPTY_2.0/main.py`.
- **prompty** (antes *PROMPTY_2.5*): versión modular con soporte de voz. Ahora puede instalarse como paquete y ejecutarse con `python -m prompty`.

Asegúrate de usar Python 3.13

## Instalación

1. Clona este repositorio.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. (Opcional) instala el paquete en modo desarrollo para poder ejecutarlo desde cualquier lugar:
   ```bash
   pip install -e .
   ```

Una vez instalado, inicia el asistente con:
```bash
python -m prompty
```

## Estructura de carpetas
Prompty1.0.py/ # Implementación inicial con varios scripts sueltos
PROMPTY_2.0/ # Dividido en datos, funciones y utilidades
prompty/      # Organizado por capas: models, services, views

Cada carpeta contiene el código correspondiente a su versión del asistente.

PROMPTY es un asistente en desarrollo. Este repositorio contiene diferentes versiones del proyecto escritas en Python.

## Interfaz gráfica

Al ejecutar `python -m prompty` se te preguntará si deseas usar la interfaz por consola o una ventana gráfica sencilla. La versión gráfica permite escribir comandos, dictarlos por voz y ver las respuestas en pantalla.

## Licencia

Este proyecto está disponible bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más información.