import re


def interpretar(texto):
    """Devuelve (comando, argumentos, palabra_clave) a partir de una cadena.

    Si no se reconoce la orden, el comando será "comando_no_reconocido",
    los argumentos serán None y la palabra clave será None.
    """
    texto = texto.lower().strip()
    texto = texto.replace("en el", "en")  # Normaliza "buscar en el navegador" → "buscar en navegador"

    texto_simple = re.sub(r"[!.,?]", "", texto).strip()

    def resultado(comando, palabra_clave=None):
        return comando, None, palabra_clave
    saludos = [
        "hola",
        "hola prompty",
        "buenos dias",
        "buenas tardes",
        "buenas noches",
        "que tal",
        "como estas",
    ]
    if texto_simple in saludos:
        return resultado("saludo", texto_simple)

    if "administrador" in texto and "funciones" in texto:
        return resultado("modo_admin", "funciones de administrador")

    if "buscar" in texto:
        if "youtube" in texto:
            return resultado("buscar_en_youtube", "youtube")
        elif "google" in texto or "navegador" in texto:
            # Si el usuario especifica google o navegador, se asume que
            # desea realizar la búsqueda directamente en ese destino.
            return resultado("buscar_en_navegador", "navegador")
        else:
            # El usuario dijo "buscar" pero no indicó destino; se pregunta dónde.
            return resultado("buscar_general", "buscar")

    if any(p in texto for p in [
        "musica",
        "música",
        "music",
        "cancion",
        "canción",
        "canciones",
    ]):
        return resultado("reproducir_musica", "musica")

    if "dia" in texto_simple or "hoy" in texto_simple:
        return resultado("dia_fecha", "dia")

    if re.search(r"\bfecha\b", texto) and re.search(r"\bhora\b", texto):
        return resultado("fecha_hora", "fecha y hora")
    if re.search(r"\bfecha\b", texto):
        return resultado("fecha", "fecha")
    if re.search(r"\bhora\b", texto):
        return resultado("hora", "hora")
    if re.search(r"\btiempo\b", texto):
        return resultado("fecha_hora", "tiempo")

    numero_comandos = {
        ("1", "uno"): "fecha_hora",
        ("2", "dos"): "abrir_con_opcion",
        ("3", "tres"): "buscar_general",
        ("4", "cuatro"): "reproducir_musica",
        ("5", "cinco"): "dato_curioso",
        ("6", "seis"): "info_programa",
        ("7", "siete"): "modo_admin",
        ("8", "ocho"): "editar_usuario",
        ("9", "nueve"): "cerrar_sesion",
        ("10", "diez"): "salir",
    }

    for claves, comando in numero_comandos.items():
        if texto in claves:
            return resultado(comando, texto)

    palabras_clave = {
        ("tiempo",): "fecha_hora",
        ("carpeta", "folder", "directorio"): "abrir_carpeta",
        ("archivo", "documento", "fichero", "aplicacion", "aplicación", "app"): "abrir_archivo",
        ("abrir", "abre", "ejecuta"): "abrir_con_opcion",
        ("youtube",): "buscar_en_youtube",
        # Si la palabra clave indica explícitamente "navegador" o "google",
        # se asume búsqueda directa en el navegador.
        ("navegador", "google", "internet", "web", "explorador"): "buscar_en_navegador",
        # Palabras genéricas para buscar sin destino definido.
        ("buscar", "investigar", "consultar"): "buscar_general",
        (
            "musica",
            "música",
            "music",
            "cancion",
            "canción",
            "canciones",
            "escuchar",
            "reproduce",
            "pon",
            "toca",
            "suena",
        ): "reproducir_musica",
        ("curioso", "dato", "curiosidad", "sabias"): "dato_curioso",
        ("programa", "creador", "información", "informacion", "acerca", "sobre"): "info_programa",
        ("usuario", "perfil", "cuenta"): "editar_usuario",
        (
            "funciones de administrador",
            "funciones del administrador",
            "abre el administrador",
            "abre las funciones de administrador",
            "abrir administrador",
            "abrir las funciones de administrador",
        ): "modo_admin",
        ("admin", "administrador"): "modo_admin",
        ("ayuda", "opciones", "menu", "ayudar"): "ayuda",
        ("tree", "árbol", "arbol", "estructura", "directorios", "mapa"): "ver_arbol",
        ("cerrar sesión", "cerrar sesion", "logout"): "cerrar_sesion",
        ("salir", "cerrar", "adios", "terminar", "exit"): "salir",
    }

    for palabras, comando in palabras_clave.items():
        coincidencia = next((p for p in palabras if p in texto), None)
        if coincidencia:
            return resultado(comando, coincidencia)

    return resultado("comando_no_reconocido")
