import os

import streamlit as st
from dotenv import load_dotenv
from openai import (
    OpenAI,
    APIError,
    AuthenticationError,
    RateLimitError,
)


# ==========================================================
# 1. CONFIGURACION INICIAL
# ==========================================================

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-6-astra")

# Solo creamos el cliente si tenemos una clave de API.
client = OpenAI(api_key=API_KEY) if API_KEY else None

st.set_page_config(
    page_title="CiscoNet",
    page_icon="🌐",
    layout="wide",
)


# ==========================================================
# 2. PERSONALIDAD Y CONOCIMIENTOS DE NUESTRA IA
# ==========================================================

SYSTEM_PROMPT = """
Eres CiscoNet, una inteligencia artificial especializada
en redes Cisco y Cisco Packet Tracer.

Tu objetivo es ayudar a los usuarios a aprender, configurar,
analizar y solucionar problemas de redes informaticas.

AREAS DE ESPECIALIZACION:

- Direccionamiento IPv4 e IPv6.
- Calculo de subredes y subnetting.
- Routers y switches Cisco.
- VLAN y enlaces trunk.
- Enrutamiento estatico.
- RIP, OSPF y otros protocolos de enrutamiento.
- DHCP y DNS.
- STP y EtherChannel.
- ACL y NAT.
- Modelo OSI y modelo TCP/IP.
- Diagnostico de conectividad.
- Comandos Cisco IOS.
- Practicas de CCNA y Cisco Packet Tracer.

REGLAS DE COMPORTAMIENTO:

1. Responde en espanol.
2. Explica los procedimientos paso a paso.
3. Usa comandos Cisco IOS cuando sean pertinentes.
4. Explica que hace cada comando importante.
5. Separa las configuraciones por dispositivo.
6. No inventes topologias, interfaces ni direcciones IP.
7. Si falta informacion, pregunta al usuario o declara
   claramente las suposiciones que estas utilizando.
8. Cuando diagnostiques un error, diferencia las causas
   posibles de los problemas que realmente se han confirmado.
9. Indica como comprobar si una solucion funciona.
10. Prioriza las soluciones compatibles con las funciones
    disponibles en el dispositivo y en Packet Tracer.
11. Si un cambio puede interrumpir la conectividad,
    explica el riesgo antes de recomendar aplicarlo.
12. No afirmes que has accedido a Packet Tracer, ejecutado
    comandos o comprobado una topologia si no lo has hecho.

FORMATO DE DIAGNOSTICO:

Cuando el usuario presente un problema de red, intenta
organizar la respuesta en estas secciones:

1. Problema observado.
2. Posibles causas.
3. Informacion que necesitamos comprobar.
4. Procedimiento de solucion.
5. Comandos de verificacion.
6. Explicacion del resultado esperado.

Adapta la profundidad de las respuestas al nivel del usuario.
Tu prioridad es ensenar a comprender las redes, no solo
entregar comandos.
"""


# ==========================================================
# 3. BARRA LATERAL
# ==========================================================

with st.sidebar:

    st.title("CiscoNet")
    st.caption("Asistente inteligente de redes")

    st.divider()

    st.subheader("Estado del sistema")

    if client:
        st.success("Conexion con la API configurada")
        st.caption(f"Modelo: {MODEL}")
    else:
        st.warning("Falta configurar la API")
        st.caption(
            "Necesitas configurar OPENAI_API_KEY "
            "en el archivo .env para activar la IA."
        )

    st.divider()

    st.subheader("Funciones del proyecto")

    st.write("💬 Consultas sobre redes Cisco")
    st.write("⚙️ Generacion de configuraciones")
    st.write("🔎 Diagnostico de problemas")
    st.write("📚 Aprendizaje de CCNA")

    st.divider()

    st.caption(
        "Version 0.1: asistente conversacional."
    )

    if st.button(
        "Limpiar conversacion",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.rerun()


# ==========================================================
# 4. INTERFAZ PRINCIPAL
# ==========================================================

st.title("🌐 CiscoNet")

st.markdown(
    """
    ### Tu asistente especializado en redes Cisco

    Pregunta sobre configuraciones, protocolos, direccionamiento
    IP o problemas que encuentres en tus laboratorios.
    """
)

st.info(
    "Esta version todavia no accede directamente a Packet Tracer. "
    "Por ahora, puedes consultar y aprender sobre redes."
)


# ==========================================================
# 5. HISTORIAL DE CONVERSACION
# ==========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# Mostrar los mensajes anteriores.
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ==========================================================
# 6. ENTRADA DEL USUARIO
# ==========================================================

prompt = st.chat_input(
    "Ejemplo: ¿Como configuro dos VLAN en un switch Cisco?"
)


# ==========================================================
# 7. PROCESAMIENTO DE LA CONSULTA
# ==========================================================

if prompt:

    # Guardar y mostrar la pregunta.
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # Preparar la respuesta de la IA.
    with st.chat_message("assistant"):

        if client is None:

            answer = (
                "Todavia no tengo configurada la conexion con "
                "el modelo de inteligencia artificial.\n\n"
                "Configura OPENAI_API_KEY y OPENAI_MODEL "
                "en tu archivo .env. Despues reinicia la aplicacion."
            )

            st.warning(answer)

        else:

            try:

                with st.spinner(
                    "CiscoNet esta analizando tu consulta..."
                ):

                    # Enviar la conversacion al modelo.
                    response = client.responses.create(
                        model=MODEL,
                        instructions=SYSTEM_PROMPT,
                        input=st.session_state.messages[-20:],
                    )

                    answer = response.output_text

                    if not answer:
                        answer = (
                            "El modelo no devolvio texto. "
                            "Intenta formular la pregunta nuevamente."
                        )

            except AuthenticationError:

                answer = (
                    "Error de autenticacion: revisa que tu "
                    "clave de API sea correcta y este activa."
                )

            except RateLimitError:

                answer = (
                    "Se ha alcanzado un limite de uso o cuota "
                    "de la API. Revisa el estado de tu cuenta."
                )

            except APIError:

                answer = (
                    "La API devolvio un error. Comprueba que el "
                    "modelo configurado este disponible para tu "
                    "cuenta y vuelve a intentarlo."
                )

            except Exception:

                answer = (
                    "No se pudo completar la consulta. "
                    "Comprueba tu conexion, la configuracion "
                    "del proyecto y el acceso a la API."
                )

            # Mostrar la respuesta.
            st.markdown(answer)

    # Guardar la respuesta en el historial.
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )