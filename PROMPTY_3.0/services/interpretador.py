import re
from typing import Dict, Optional, Tuple

from services.comandos_basicos import ComandosBasicos


_basicos = ComandosBasicos()


def _extraer_busqueda(texto: str) -> Tuple[Optional[str], Optional[str]]:
    """Identifica la búsqueda solicitada y su posible destino."""

    patron = re.search(
        r"b[uú]sca(?:r)?(?:me|nos|le)?\s+(?P<termino>.+?)(?:\s+en\s+(?P<destino>youtube|google|navegador|internet|web|musica|música|music))?$",
        texto,
    )
    if patron:
        termino = patron.group("termino")
        destino = patron.group("destino")
        return termino.strip(), (destino or "").strip()
    return None, None


def _extraer_reproduccion(texto: str) -> Optional[str]:
    """Detecta peticiones de reproducción de música con lenguaje natural."""

    patron = re.search(
        r"(?:pon|ponme|reproduce|toca|coloca|escuchar|quiero escuchar|pone)\s+(?P<cancion>.+)",
        texto,
    )
    if patron:
        return patron.group("cancion").strip()
    return None


def _normalizar_texto(texto: str) -> str:
    """Convierte a minúsculas y recorta espacios innecesarios."""

    return texto.lower().strip()


def interpretar(texto):
    """Devuelve (comando, argumentos, palabra_clave) a partir de una cadena.

    Si no se reconoce la orden, el comando será "comando_no_reconocido",
    los argumentos serán None y la palabra clave será None.
    """

    texto = _normalizar_texto(texto)
    texto = texto.replace("en el", "en")  # Normaliza "buscar en el navegador" → "buscar en navegador"

    texto_simple = re.sub(r"[!.,?]", "", texto).strip()

    def resultado(comando, palabra_clave=None, argumentos: Optional[Dict[str, str]] = None):
        return comando, argumentos, palabra_clave

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

    termino_busqueda, destino_busqueda = _extraer_busqueda(texto)

    if termino_busqueda and not destino_busqueda:
        destino_detectado = re.match(
            r"en\s+(youtube|google|navegador|internet|web|musica|música|music)\b(?:\s+(?P<resto>.+))?$",
            termino_busqueda,
        )
        if destino_detectado:
            destino_busqueda = destino_detectado.group(1)
            termino_busqueda = destino_detectado.group("resto")
            if termino_busqueda:
                termino_busqueda = termino_busqueda.strip()

    if termino_busqueda:
        destino_busqueda = destino_busqueda or ""
        if "youtube" in destino_busqueda:
            return resultado(
                "buscar_en_youtube",
                "youtube",
                {"termino": termino_busqueda},
            )
        if destino_busqueda in ("google", "navegador", "internet", "web"):
            return resultado(
                "buscar_en_navegador",
                destino_busqueda or "navegador",
                {"termino": termino_busqueda},
            )
        if destino_busqueda in ("musica", "música", "music"):
            return resultado(
                "reproducir_musica",
                destino_busqueda,
                {"termino": termino_busqueda},
            )
        return resultado(
            "buscar_general",
            "buscar",
            {"termino": termino_busqueda},
        )

    cancion = _extraer_reproduccion(texto)
    if cancion:
        return resultado("reproducir_musica", "musica", {"termino": cancion})

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


def _normalizar_argumento(argumento: Optional[str]) -> Optional[str]:
    if isinstance(argumento, str):
        argumento = argumento.strip()
        return argumento or None
    return None


def _entrada_silenciosa(_: str = "") -> str:
    """Devuelve cadena vacía para evitar prompts interactivos en API."""

    return ""


def obtener_hora() -> str:
    return _basicos.mostrar_hora()


def obtener_fecha() -> str:
    return _basicos.mostrar_fecha()


def obtener_fecha_hora() -> str:
    return _basicos.mostrar_fecha_hora()


def abrir_navegador(busqueda: Optional[str] = None, url: Optional[str] = None) -> str:
    termino = _normalizar_argumento(busqueda)
    return _basicos.buscar_en_navegador_con_opcion(
        destino_predefinido="navegador",
        entrada_manual_func=_entrada_silenciosa,
        termino=termino,
        url=url,
    )


def buscar_youtube(busqueda: Optional[str] = None, url: Optional[str] = None) -> str:
    termino = _normalizar_argumento(busqueda)
    return _basicos.buscar_en_navegador_con_opcion(
        destino_predefinido="youtube",
        entrada_manual_func=_entrada_silenciosa,
        termino=termino,
        url=url,
    )


def reproducir_musica(busqueda: Optional[str] = None, url: Optional[str] = None) -> str:
    termino = _normalizar_argumento(busqueda)
    return _basicos.reproducir_musica(
        entrada_manual_func=_entrada_silenciosa,
        termino=termino,
        url=url,
    )


def abrir_carpeta(ruta: Optional[str] = None) -> str:
    ruta_normalizada = _normalizar_argumento(ruta)
    if ruta_normalizada:
        return _basicos.abrir_carpeta(ruta_normalizada)
    return _basicos.abrir_con_opcion(tipo="carpeta", entrada_manual_func=_entrada_silenciosa)


def abrir_archivo(ruta: Optional[str] = None) -> str:
    ruta_normalizada = _normalizar_argumento(ruta)
    if ruta_normalizada:
        return _basicos.abrir_carpeta(ruta_normalizada)
    return _basicos.abrir_con_opcion(
        tipo="archivo",
        entrada_manual_func=_entrada_silenciosa,
    )


def dato_curioso() -> str:
    return _basicos.mostrar_dato_curioso()


def informacion(opcion: Optional[str] = None) -> str:
    seleccion = _normalizar_argumento(opcion) or "2"
    return _basicos.info_sistema(entrada_manual_func=lambda _: seleccion)


def salir() -> str:
    return "👋 Hasta pronto."


def interpretar_intencion_local(texto: str) -> Tuple[Optional[str], Optional[str]]:
    """Usa el interpretador clásico para mapear el mensaje a una intención y argumento."""

    comando, argumentos, palabra_clave = interpretar(texto)

    if comando in {"hora", "fecha", "fecha_hora", "dia_fecha"}:
        return comando, None
    if comando in {"buscar_en_youtube", "buscar_general", "buscar_en_navegador"}:
        if isinstance(argumentos, dict):
            return comando, argumentos.get("termino")
        return comando, palabra_clave
    if comando == "reproducir_musica":
        if isinstance(argumentos, dict):
            return comando, argumentos.get("termino")
        return comando, palabra_clave
    if comando in {"abrir_carpeta", "abrir_archivo", "abrir_con_opcion"}:
        return comando, palabra_clave
    if comando in {"dato_curioso", "info_programa", "salir", "saludo"}:
        return comando, None
    return None, None


def ejecutar_intencion(intencion: Optional[str], argumento: Optional[str] = None) -> Tuple[str, bool]:
    """Ejecuta la intención solicitada y devuelve el texto y si fue exitosa."""

    accion = (intencion or "").strip().lower()
    texto: str

    if accion in {"hora"}:
        texto = obtener_hora()
    elif accion in {"fecha"}:
        texto = obtener_fecha()
    elif accion in {"fecha_hora", "dia_fecha"}:
        texto = obtener_fecha_hora()
    elif accion in {"abrir_navegador", "buscar_en_navegador", "buscar_general"}:
        texto = abrir_navegador(argumento)
    elif accion in {"buscar_youtube", "buscar_en_youtube"}:
        texto = buscar_youtube(argumento)
    elif accion == "reproducir_musica":
        texto = reproducir_musica(argumento)
    elif accion in {"abrir_carpeta"}:
        texto = abrir_carpeta(argumento)
    elif accion in {"abrir_archivo", "abrir_con_opcion"}:
        texto = abrir_archivo(argumento)
    elif accion in {"dato_curioso"}:
        texto = dato_curioso()
    elif accion in {"informacion", "info_programa"}:
        texto = informacion(argumento)
    elif accion in {"salir"}:
        texto = salir()
    elif accion in {"saludo"}:
        texto = _basicos.responder_saludo()
    else:
        texto = "❌ No pude reconocer la acción solicitada."

    exito = not texto.strip().startswith("❌")
    return texto, exito
