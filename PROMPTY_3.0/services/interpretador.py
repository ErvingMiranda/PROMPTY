def interpretar(texto):
    """Devuelve (comando, argumentos) a partir de una cadena.

    Si no se reconoce la orden, el comando será "comando_no_reconocido"
    y los argumentos serán None.
    """
    texto = texto.lower().strip()
    texto = texto.replace("en el", "en")  # Normaliza "buscar en el navegador" → "buscar en navegador"

    if "buscar" in texto:
        if "youtube" in texto:
            return "buscar_en_youtube", None
        elif "google" in texto or "navegador" in texto:
            # Si el usuario especifica google o navegador, ya sabemos el destino
            # por lo que sólo se debe preguntar si quiere buscar un término o
            # ingresar una URL.
            return "buscar_general", None
        else:
            # El usuario dijo "buscar" pero no indicó destino; se pregunta dónde.
            return "buscar_en_navegador", None

    if any(p in texto for p in [
        "musica",
        "música",
        "music",
        "cancion",
        "canción",
        "canciones",
    ]):
        return "reproducir_musica", None

    numero_comandos = {
        ("1", "uno"): "fecha_hora",
        ("2", "dos"): "abrir_con_opcion",
        ("3", "tres"): "buscar_en_navegador",
        ("4", "cuatro"): "reproducir_musica",
        ("5", "cinco"): "dato_curioso",
        ("6", "seis"): "info_programa",
        ("7", "siete", "administrador", "modo admin"): "modo_admin",
        ("8", "ocho"): "editar_usuario",
        ("9", "nueve", "cerrar sesión", "cerrar sesion", "logout"): "cerrar_sesion",
        ("10", "diez", "salir", "cerrar"): "salir",
    }

    for claves, comando in numero_comandos.items():
        if texto in claves:
            return comando, None

    palabras_clave = {
        ("hora", "fecha"): "fecha_hora",
        ("carpeta",): "abrir_carpeta",
        ("archivo",): "abrir_archivo",
        ("abrir",): "abrir_con_opcion",
        ("youtube",): "buscar_en_youtube",
        ("navegador", "google"): "buscar_en_navegador",
        ("buscar",): "buscar_general",
        (
            "musica",
            "música",
            "music",
            "cancion",
            "canción",
            "canciones",
        ): "reproducir_musica",
        ("curioso", "dato"): "dato_curioso",
        ("programa", "creador", "información"): "info_programa",
        ("usuario", "perfil"): "editar_usuario",
        ("ayuda", "opciones", "menu"): "ayuda",
        ("salir", "cerrar"): "salir",
        ("cerrar sesión", "cerrar sesion", "logout"): "cerrar_sesion",
    }

    for palabras, comando in palabras_clave.items():
        if any(p in texto for p in palabras):
            return comando, None

    return "comando_no_reconocido", None
