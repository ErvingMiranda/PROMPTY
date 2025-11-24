import re
from typing import Dict, Optional, Tuple


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
            r"en\s+(youtube|google|navegador|internet|web|musica|música|music)\b",
            termino_busqueda,
        )
        if destino_detectado:
            termino_busqueda = None
            destino_busqueda = destino_detectado.group(1)

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
