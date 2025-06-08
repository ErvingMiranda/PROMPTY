def interpretar(texto):
    texto = texto.lower().strip()

    # Comandos por número
    if texto in ["1", "uno"]:
        return "fecha_hora", None
    if texto in ["2", "dos"]:
        return "abrir_con_opcion", None
    if texto in ["3", "tres"]:
        return "buscar_en_navegador", None
    if texto in ["4", "cuatro"]:
        return "dato_curioso", None
    if texto in ["5", "cinco"]:
        return "info_programa", None
    if texto in ["6", "seis", "salir", "cerrar"]:
        return "salir", None
    if texto in ["7", "siete", "administrador", "modo admin"]:
        return "modo_admin", None
    if texto in ["ayuda", "menu", "opciones"]:
        return "ayuda", None

    # Comandos por palabra clave
    if "hora" in texto or "fecha" in texto:
        return "fecha_hora", None
    if "carpeta" in texto or "archivo" in texto or "abrir" in texto:
        return "abrir_con_opcion", None
    if "youtube" in texto:
        return "buscar_en_youtube", None
    if "navegador" in texto or "buscar" in texto:
        return "buscar_en_navegador", None
    if "curioso" in texto or "dato" in texto:
        return "dato_curioso", None
    if "programa" in texto or "creador" in texto or "información" in texto:
        return "info_programa", None
    if "configurar" in texto or "voz" in texto:
        return "configurar_voz", None
    if "salir" in texto or "cerrar" in texto:
        return "salir", None

    return "comando_no_reconocido", None