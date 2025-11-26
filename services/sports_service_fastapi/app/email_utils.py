# services/sports_service_fastapi/app/email_utils.py

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from dotenv import load_dotenv

# =========================
#  Charger les variables du fichier .env à la racine
#  .../PrjBackendRCWSportConnectIA/.env
#  (même logique que dans auth_service_fastapi)
# =========================
ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(ROOT_ENV)

# Configuration de l’envoi d’e-mails (depuis le .env)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))  # 587 = TLS
SMTP_USER = os.getenv("SMTP_USER")  # adresse e-mail de l’application
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")      # mot de passe ou app password
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER) # adresse visible par le client


def build_daily_summary_message(
    client_name: str,
    checklist: list[str],
    evolution_text: str,
) -> str:
    """
    Construit le contenu du message :
    - nom du client
    - checklist du jour
    - résumé de l'évolution
    """

    lines = [
        f"Bonjour {client_name},",
        "",
        "Voici le résumé de votre journée d’entraînement :",
        "",
        "✅ Checklist du jour :",
    ]

    for item in checklist:
        lines.append(f"  - {item}")

    lines += [
        "",
        "📈 Évolution d’aujourd’hui :",
        evolution_text,
        "",
        "Continuez comme ça ! Si vous avez des questions, n'hésitez pas à contacter votre coach 😊",
        "",
        "Équipe SportConnectIA",
    ]

    # Retourne toutes les lignes sous forme d’un texte unique
    return "\n".join(lines)


def send_daily_summary_email(
    to_email: str,
    client_name: str,
    checklist: list[str],
    evolution_text: str,
) -> None:
    """
    Envoie un e-mail au client en utilisant le protocole SMTP.
    """

    if not (SMTP_USER and SMTP_PASSWORD):
        # Éviter une erreur silencieuse si .env n’est pas configuré
        raise RuntimeError(
            "SMTP_USER ou SMTP_PASSWORD n’est pas défini dans le fichier .env. "
            "Veuillez configurer ces variables avant d’envoyer des e-mails."
        )

    # 1) Construire le texte du message
    body_text = build_daily_summary_message(
        client_name=client_name,
        checklist=checklist,
        evolution_text=evolution_text,
    )

    # 2) Créer l’objet du message (MIME)
    msg = MIMEMultipart()
    msg["Subject"] = "Résumé de votre journée d’entraînement - SportConnectIA"
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email

    # Ajouter le corps du message (texte brut)
    msg.attach(MIMEText(body_text, "plain", "utf-8"))

    # 3) Connexion au serveur SMTP et envoi du message
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()  # active la connexion sécurisée TLS
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
