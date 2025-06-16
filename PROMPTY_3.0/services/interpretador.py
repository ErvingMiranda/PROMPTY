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
            return "buscar_en_navegador", None
        else:
            return "buscar_general", None

    numero_comandos = {
        ("1", "uno"): "fecha_hora",
        ("2", "dos"): "abrir_con_opcion",
        ("3", "tres"): "buscar_en_navegador",
        ("4", "cuatro"): "dato_curioso",
        ("5", "cinco"): "info_programa",
        ("6", "seis", "administrador", "modo admin"): "modo_admin",
        ("7", "siete"): "editar_usuario",
        ("8", "ocho", "cerrar sesión", "cerrar sesion", "logout"): "cerrar_sesion",
        ("9", "nueve", "salir", "cerrar"): "salir",
    }

    for claves, comando in numero_comandos.items():
        if texto in claves:
            return comando, None

    palabras_clave = {
        ("hora", "fecha"): "fecha_hora",
        ("carpeta", "archivo", "abrir"): "abrir_con_opcion",
        ("youtube",): "buscar_en_youtube",
        ("navegador", "google"): "buscar_en_navegador",
        ("buscar",): "buscar_general",
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
