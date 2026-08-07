"""
Tool: send_vehicle_images_whatsapp

Por que existe:
  WhatsApp no interpreta Markdown (![...]()) ni HTML (<img>) dentro del texto
  del bot -- lo probamos y el usuario ve el texto literal, no una foto. La
  UNICA forma de que aparezca como una imagen real en WhatsApp es enviando un
  mensaje de tipo "media" a traves de la API de Twilio (parametro media_url),
  por fuera del texto de respuesta del agente.

Que hace:
  1. Lee del contexto de la conversacion (que watsonx Orchestrate inyecta
     automaticamente para el canal WhatsApp) el numero del usuario y el
     numero del agente:
       context.whatsapp.user_phone_number
       context.whatsapp.agent_phone_number
     Documentado en:
     https://www.ibm.com/docs/en/watsonx/watson-orchestrate/base?topic=channels-channel-specific-context-variables
  2. Si la conversacion NO viene por WhatsApp, no hace nada y devuelve
     sent=False con reason="not_whatsapp_channel" -- en ese caso el agente
     debe usar el flujo normal (Markdown en el chat).
  3. Si viene por WhatsApp, usa el SDK de Twilio para enviar cada imagen como
     un mensaje de WhatsApp nativo (media_url), usando las mismas
     credenciales de Twilio que ya configuraste para el canal.

Conexion necesaria (crearla antes de importar la tool):

  app_id="twilio_whatsapp_api"
  Tipo: Key Value, con las claves:
    account_sid  -> el mismo Account SID que usaste al crear el canal Twilio WhatsApp
    auth_token   -> el mismo Auth Token que usaste al crear el canal Twilio WhatsApp

Import de la tool (CLI del ADK):

  orchestrate tools import -k python \
      -f send_vehicle_images_whatsapp_tool.py \
      -r requirements_whatsapp.txt \
      -a twilio_whatsapp_api

Testeo local (emulando la conexion):

  export WXO_SECURITY_SCHEMA_twilio_whatsapp_api=key_value_creds
  export WXO_CONNECTION_twilio_whatsapp_api_account_sid=ACxxxxxxxx
  export WXO_CONNECTION_twilio_whatsapp_api_auth_token=xxxxxxxx
"""

from typing import List

from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.run import connections
from ibm_watsonx_orchestrate.run.context import AgentRun

TWILIO_APP_ID = "twilio_whatsapp_api"


@tool(
    name="send_vehicle_images_whatsapp",
    description=(
        "Envia una o mas imagenes de un vehiculo como mensajes de imagen "
        "NATIVOS de WhatsApp (usando Twilio), para que el usuario las vea como "
        "fotos reales en el chat. Solo funciona si la conversacion actual es "
        "por el canal de WhatsApp; si no lo es, no envia nada y lo informa."
    ),
    expected_credentials=[
        {"app_id": TWILIO_APP_ID, "type": ConnectionType.KEY_VALUE},
    ],
)
def send_vehicle_images_whatsapp(context: AgentRun, image_urls: List[str]) -> dict:
    """Envia imagenes de un vehiculo como mensajes nativos de WhatsApp via Twilio.

    Args:
        context (AgentRun): Contexto de ejecucion inyectado automaticamente por
            Orchestrate. No lo completa el agente/usuario.
        image_urls (List[str]): Lista de URLs publicas de las imagenes a enviar
            (por ejemplo, las obtenidas del campo images[].image_url que
            devuelve la tool "Obtener un vehiculo por su ID").

    Returns:
        dict: {
            "sent": bool,
            "reason": str | None,       # motivo cuando sent=False
            "message_sids": [str, ...], # ids de Twilio de los mensajes enviados
            "count": int,
        }
    """
    if not image_urls:
        return {"sent": False, "reason": "no_image_urls", "message_sids": [], "count": 0}

    req_context = context.request_context
    channel = req_context.get("channel") or {}

    if channel.get("channel_type") != "whatsapp":
        return {
            "sent": False,
            "reason": "not_whatsapp_channel",
            "message_sids": [],
            "count": 0,
        }

    whatsapp_ctx = channel.get("whatsapp") or {}
    to_number = whatsapp_ctx.get("user_phone_number")
    from_number = whatsapp_ctx.get("agent_phone_number")

    if not to_number or not from_number:
        return {
            "sent": False,
            "reason": "missing_phone_numbers",
            "message_sids": [],
            "count": 0,
        }

    creds = connections.key_value(TWILIO_APP_ID)
    account_sid = creds.get("account_sid")
    auth_token = creds.get("auth_token")

    from twilio.rest import Client

    client = Client(account_sid, auth_token)

    message_sids = []
    for url in image_urls:
        message = client.messages.create(
            from_=f"whatsapp:{from_number}",
            to=f"whatsapp:{to_number}",
            media_url=[url],
        )
        message_sids.append(message.sid)

    return {
        "sent": True,
        "reason": None,
        "message_sids": message_sids,
        "count": len(message_sids),
    }