import re


def interpretar(texto):
    """Devuelve (comando, argumentos) a partir de una cadena.

    Si no se reconoce la orden, el comando será "comando_no_reconocido"
    y los argumentos serán None.
    """
    texto = texto.lower().strip()
    texto = texto.replace("en el", "en")  # Normaliza "buscar en el navegador" → "buscar en navegador"

    texto_simple = re.sub(r"[!.,?]", "", texto).strip()
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
        return "saludo", None

    if "administrador" in texto and "funciones" in texto:
        return "modo_admin", None

    if "buscar" in texto:
        if "youtube" in texto:
            return "buscar_en_youtube", None
        elif "google" in texto or "navegador" in texto:
            # Si el usuario especifica google o navegador, se asume que
            # desea realizar la búsqueda directamente en ese destino.
            return "buscar_en_navegador", None
        else:
            # El usuario dijo "buscar" pero no indicó destino; se pregunta dónde.
            return "buscar_general", None

    if any(p in texto for p in [
        "musica",
        "música",
        "music",
        "cancion",
        "canción",
        "canciones",
    ]):
        return "reproducir_musica", None

    if "dia" in texto_simple or "hoy" in texto_simple:
        return "dia_fecha", None

    if re.search(r"\bfecha\b", texto) and re.search(r"\bhora\b", texto):
        return "fecha_hora", None
    if re.search(r"\bfecha\b", texto):
        return "fecha", None
    if re.search(r"\bhora\b", texto):
        return "hora", None
    if re.search(r"\btiempo\b", texto):
        return "fecha_hora", None

    numero_comandos = {
        ("1", "uno"): "fecha_hora",
        ("2", "dos"): "abrir_con_opcion",
        ("3", "tres"): "buscar_en_navegador",
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
            return comando, None

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
        if any(p in texto for p in palabras):
            return comando, None

    return "comando_no_reconocido", None
