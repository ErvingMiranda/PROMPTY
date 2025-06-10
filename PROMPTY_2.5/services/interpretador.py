def interpretar(texto):
    texto = texto.lower().strip()

    numero_comandos = {
        ("1", "uno"): "fecha_hora",
        ("2", "dos"): "abrir_con_opcion",
        ("3", "tres"): "buscar_en_navegador",
        ("4", "cuatro"): "dato_curioso",
        ("5", "cinco"): "info_programa",
        ("6", "seis", "salir", "cerrar"): "salir",
        ("7", "siete", "administrador", "modo admin"): "modo_admin",
        ("8", "ocho"): "editar_usuario",
        ("9", "nueve", "cerrar sesión", "cerrar sesion", "logout"): "cerrar_sesion",
        ("ayuda", "menu", "opciones"): "ayuda",
    }

    for claves, comando in numero_comandos.items():
        if texto in claves:
            return comando, None

    palabras_clave = {
        ("hora", "fecha"): "fecha_hora",
        ("carpeta", "archivo", "abrir"): "abrir_con_opcion",
        ("youtube",): "buscar_en_youtube",
        ("navegador", "buscar"): "buscar_en_navegador",
        ("curioso", "dato"): "dato_curioso",
        ("programa", "creador", "información"): "info_programa",
        ("usuario", "perfil"): "editar_usuario",
        ("salir", "cerrar"): "salir",
        ("cerrar sesión", "cerrar sesion", "logout"): "cerrar_sesion",
    }

    for palabras, comando in palabras_clave.items():
        if any(p in texto for p in palabras):
            return comando, None

    return "comando_no_reconocido", None
