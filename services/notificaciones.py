"""Requerimiento 8: alertas con Twilio y correos con Brevo API / SMTP."""
import os, smtplib, base64
import requests as _requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def enviar_alerta_sms(mensaje: str):
    sid   = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")
    if not sid or not token:
        print("[Twilio] No configurado, se omite SMS")
        return
    try:
        from twilio.rest import Client
        twilio_from = os.getenv("TWILIO_FROM", "")
        admin_phone = os.getenv("TWILIO_ADMIN_PHONE", "")
        # Si el número FROM es el sandbox de WhatsApp, usar formato whatsapp:
        if twilio_from == "+14155238886":
            twilio_from = f"whatsapp:{twilio_from}"
            admin_phone = f"whatsapp:{admin_phone}"
        Client(sid, token).messages.create(
            body=mensaje,
            from_=twilio_from,
            to=admin_phone,
        )
        print("[Twilio] Alerta enviada")
    except Exception as e:
        print(f"[Twilio] Error enviando SMS: {e}")

def _cuerpo_email(usuario, compra):
    detalle = "\n".join(
        f"  - {i['nombre']} x{i['cantidad']}  ${i['subtotal']:.2f}" for i in compra.items
    )
    return (
        f"Hola {usuario.nombre},\n\n"
        f"Gracias por tu compra #{compra.id}.\n\n{detalle}\n\n"
        f"Subtotal: ${float(compra.subtotal):.2f}\n"
        f"IVA 15%:  ${float(compra.iva):.2f}\n"
        f"TOTAL:    ${float(compra.total):.2f}\n\n"
        f"Estado: {compra.estado}\nClave de acceso: {compra.clave_acceso}\n\n"
        f"Se adjunta la factura electrónica en XML.\nTechStore 360"
    )

def enviar_factura_email(usuario, compra, xml_factura: str | None):
    brevo_key = os.getenv("BREVO_API_KEY")
    if brevo_key:
        _enviar_brevo_api(brevo_key, usuario, compra, xml_factura)
    elif os.getenv("SMTP_HOST"):
        _enviar_smtp(usuario, compra, xml_factura)
    else:
        print("[Email] No configurado, se omite correo")

def _enviar_brevo_api(api_key, usuario, compra, xml_factura):
    payload = {
        "sender":  {"email": os.getenv("SMTP_FROM", "andrade73321@gmail.com")},
        "to":      [{"email": usuario.email, "name": usuario.nombre}],
        "subject": f"TechStore 360 - Factura de la compra #{compra.id}",
        "textContent": _cuerpo_email(usuario, compra),
    }
    if xml_factura:
        payload["attachment"] = [{
            "content": base64.b64encode(xml_factura.encode("utf-8")).decode(),
            "name": f"factura_{compra.id}.xml",
        }]
    try:
        r = _requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers={"api-key": api_key, "Content-Type": "application/json"},
            timeout=15,
        )
        if r.status_code in (200, 201):
            print(f"[Email] OK (Brevo API) - Factura enviada a {usuario.email}")
        else:
            print(f"[Email] ERROR Brevo API {r.status_code}: {r.text}")
    except Exception as e:
        print(f"[Email] ERROR Brevo API: {e}")

def _enviar_smtp(usuario, compra, xml_factura):
    host = os.getenv("SMTP_HOST")
    msg = MIMEMultipart()
    msg["From"]    = os.getenv("SMTP_FROM")
    msg["To"]      = usuario.email
    msg["Subject"] = f"TechStore 360 - Factura de la compra #{compra.id}"
    msg.attach(MIMEText(_cuerpo_email(usuario, compra), "plain", "utf-8"))
    if xml_factura:
        adj = MIMEApplication(xml_factura.encode("utf-8"), _subtype="xml")
        adj.add_header("Content-Disposition", "attachment",
                       filename=f"factura_{compra.id}.xml")
        msg.attach(adj)
    server = None
    try:
        server = smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587")), timeout=10)
        server.starttls()
        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
        server.send_message(msg)
        print(f"[Email] OK (SMTP) - Factura enviada a {usuario.email}")
    except Exception as e:
        print(f"[Email] ERROR SMTP: {e}")
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass
