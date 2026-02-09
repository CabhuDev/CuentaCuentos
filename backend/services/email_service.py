"""
Servicio de envío de emails usando Brevo (anteriormente Sendinblue).
Utiliza templates configurados en el dashboard de Brevo para emails profesionales.
"""

import requests
from typing import Optional, Dict, Any
from config import (
    BREVO_API_KEY, 
    BREVO_SENDER_EMAIL, 
    BREVO_SENDER_NAME, 
    BREVO_LIST_ID,
    BREVO_WELCOME_TEMPLATE_ID,
    BREVO_CHANGEPASS_TEMPLATE_ID,
    FRONTEND_URL
)


def _send_template_email(
    email: str,
    name: str,
    template_id: str,
    params: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Función genérica para enviar emails usando templates de Brevo.
    Los templates se configuran en el dashboard de Brevo con variables dinámicas.
    
    Args:
        email: Email del destinatario
        name: Nombre del destinatario
        template_id: ID del template configurado en Brevo
        params: Parámetros variables para el template (ej: {"USERNAME": "Juan"})
        
    Returns:
        bool: True si el email se envió correctamente, False en caso contrario
    """
    if not BREVO_API_KEY:
        print("⚠️ BREVO_API_KEY no configurada. Email no enviado.")
        return False
    
    if not template_id:
        print("⚠️ Template ID no configurado. Email no enviado.")
        return False
    
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }
    
    # Usar template de Brevo con parámetros dinámicos
    data = {
        "to": [{"email": email, "name": name}],
        "templateId": int(template_id),
        "params": params or {}
    }
    
    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 201:
            print(f"✅ Email (template {template_id}) enviado a {email}")
            return True
        else:
            print(f"❌ Error al enviar email: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción al enviar email: {str(e)}")
        return False


def add_contact_to_list(email: str, name: str, attributes: Optional[Dict[str, Any]] = None) -> bool:
    """
    Añade un contacto a la lista de Brevo.
    
    Args:
        email: Email del contacto
        name: Nombre del contacto
        attributes: Atributos adicionales (ej: {"REGISTRATION_DATE": "2026-02-09"})
        
    Returns:
        bool: True si el contacto se añadió correctamente
    """
    if not BREVO_API_KEY or not BREVO_LIST_ID:
        print("⚠️ BREVO_API_KEY o BREVO_LIST_ID no configurados.")
        return False
    
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }
    
    # Separar nombre en firstName y lastName
    name_parts = name.split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""
    
    data = {
        "email": email,
        "attributes": {
            "FIRSTNAME": first_name,
            "LASTNAME": last_name,
            **(attributes or {})
        },
        "listIds": [int(BREVO_LIST_ID)],
        "updateEnabled": True
    }
    
    try:
        response = requests.post(
            "https://api.brevo.com/v3/contacts",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code in [201, 204]:
            print(f"✅ Contacto {email} añadido a lista")
            return True
        else:
            print(f"⚠️ No se pudo añadir contacto: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción al añadir contacto: {str(e)}")
        return False


def send_welcome_email(email: str, username: str) -> bool:
    """
    Envía email de bienvenida usando template de Brevo (ID: BREVO_WELCOME_TEMPLATE_ID).
    
    Args:
        email: Email del nuevo usuario
        username: Nombre de usuario
        
    Returns:
        bool: True si el email se envió correctamente
    """
    params = {
        "USERNAME": username,
        "FRONTEND_URL": FRONTEND_URL
    }
    
    success = _send_template_email(
        email=email,
        name=username,
        template_id=BREVO_WELCOME_TEMPLATE_ID,
        params=params
    )
    
    # Opcionalmente añadir a lista de contactos
    if success and BREVO_LIST_ID:
        from datetime import datetime
        add_contact_to_list(
            email=email,
            name=username,
            attributes={"REGISTRATION_DATE": datetime.now().strftime("%Y-%m-%d")}
        )
    
    return success


def send_password_reset_email(email: str, username: str, reset_token: str) -> bool:
    """
    Envía un email con el enlace para resetear la contraseña.
    Usa HTML inline (puede migrarse a template de Brevo posteriormente).
    
    Args:
        email: Email del destinatario
        username: Nombre de usuario
        reset_token: Token único para el reset de contraseña
        
    Returns:
        bool: True si el email se envió correctamente
    """
    if not BREVO_API_KEY:
        print("⚠️ BREVO_API_KEY no configurada. Email no enviado.")
        return False
        
    reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token}"
    
    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }
    
    data = {
        "sender": {
            "name": BREVO_SENDER_NAME,
            "email": BREVO_SENDER_EMAIL
        },
        "to": [{"email": email, "name": username}],
        "subject": "Recuperación de Contraseña - CuentaCuentos",
        "htmlContent": f"""
        <html>
        <body>
            <h2>Hola {username},</h2>
            <p>Has solicitado restablecer tu contraseña en CuentaCuentos.</p>
            <p>Haz clic en el siguiente enlace para crear una nueva contraseña:</p>
            <p>
                <a href="{reset_url}" 
                   style="background-color: #4CAF50; color: white; padding: 14px 20px; 
                          text-decoration: none; border-radius: 4px; display: inline-block;">
                    Restablecer Contraseña
                </a>
            </p>
            <p>Este enlace expirará en 1 hora.</p>
            <p>Si no solicitaste este cambio, puedes ignorar este email.</p>
            <hr>
            <p style="color: #666; font-size: 12px;">
                CuentaCuentos - Generador de Cuentos con IA
            </p>
        </body>
        </html>
        """
    }
    
    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 201:
            print(f"✅ Email de reset enviado a {email}")
            return True
        else:
            print(f"❌ Error al enviar email: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción al enviar email: {str(e)}")
        return False


def send_password_changed_confirmation(email: str, username: str) -> bool:
    """
    Envía email de confirmación de cambio de contraseña usando template de Brevo 
    (ID: BREVO_CHANGEPASS_TEMPLATE_ID).
    
    Args:
        email: Email del usuario
        username: Nombre de usuario
        
    Returns:
        bool: True si el email se envió correctamente
    """
    from datetime import datetime
    
    params = {
        "USERNAME": username,
        "CHANGE_DATE": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "FRONTEND_URL": FRONTEND_URL
    }
    
    return _send_template_email(
        email=email,
        name=username,
        template_id=BREVO_CHANGEPASS_TEMPLATE_ID,
        params=params
    )
