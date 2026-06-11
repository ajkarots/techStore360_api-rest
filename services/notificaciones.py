"""Requerimiento 8: alertas con Twilio y correos con Brave/Brevo Email (SMTP)."""
import os, smtplib
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
        Client(sid, token).messages.create(
            body=mensaje,
            from_=os.getenv("TWILIO_FROM"),
            to=os.getenv("TWILIO_ADMIN_PHONE"),
        )
        print("[Twilio] Alerta enviada")
    except Exception as e:
        print(f"[Twilio] Error enviando SMS: {e}")

def enviar_factura_email(usuario, compra, xml_factura: str | None):
    host = os.getenv("SMTP_HOST")
    if not host:
        print("[Email] SMTP no configurado, se omite correo")
        return
    msg = MIMEMultipart()
    msg["From"] = os.getenv("SMTP_FROM")
    msg["To"] = usuario.email
    msg["Subject"] = f"TechStore 360 - Factura de la compra #{compra.id}"

    detalle = "\n".join(
        f"  - {i['nombre']} x{i['cantidad']}  ${i['subtotal']:.2f}" for i in compra.items
    )
    cuerpo = (
        f"Hola {usuario.nombre},\n\n"
        f"Gracias por tu compra #{compra.id}.\n\n{detalle}\n\n"
        f"Subtotal: ${float(compra.subtotal):.2f}\n"
        f"IVA 15%:  ${float(compra.iva):.2f}\n"
        f"TOTAL:    ${float(compra.total):.2f}\n\n"
        f"Estado: {compra.estado}\nClave de acceso: {compra.clave_acceso}\n\n"
        f"Se adjunta la factura electrónica en XML.\nTechStore 360"
    )
    msg.attach(MIMEText(cuerpo, "plain", "utf-8"))

    if xml_factura:
        adj = MIMEApplication(xml_factura.encode("utf-8"), _subtype="xml")
        adj.add_header("Content-Disposition", "attachment",
                       filename=f"factura_{compra.id}.xml")
        msg.attach(adj)

    server = None
    try:
        server = smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587")))
        server.starttls()
        server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
        server.send_message(msg)
        print(f"[Email] Factura enviada a {usuario.email}")
    finally:
        if server:
            server.quit()  # finally: liberar el recurso SMTP siempre
