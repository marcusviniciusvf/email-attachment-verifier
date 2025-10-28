import imaplib
import email
from email.header import decode_header
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import re
import hashlib 
load_dotenv()

IMAP_SERVER = os.getenv('IMAP_SERVER')
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
LAST_VERIFICATION = os.getenv('LAST_VERIFICATION')
DATE_TODAY = (datetime.now()).strftime("%d-%b-%Y")

emailDict = {
    "id": None,              # ID UNICO IMAP
    "date": None,            # DATA
    "sender": None,          # REMETENTE
    "subject": None,         # ASSUNTO
    "body": None,            # CORPO EMAIL
    "links": None,           # LINKS CONTIDOS NO BODY
    "body_Html": None,       # CORPO HTML
    "has_Attachment": False, # TEM ANEXO
    "attachments": []        # LISTA DE ANEXOS
}
emailDictChanger = emailDict.copy()
emails_List = []

PASTA_ANEXOS = "downloaded_Files"
os.makedirs(PASTA_ANEXOS, exist_ok=True)
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL_USER, EMAIL_PASS)

print(f'SINCE {LAST_VERIFICATION}')
print(type(f'SINCE {LAST_VERIFICATION}'))
print(LAST_VERIFICATION)

def print_assuntos_emails(mail):
    global emailDictChanger, emails_List
    # Buscar todos os e-mails
    print(f'SINCE {LAST_VERIFICATION}')
    print(type(f'SINCE {LAST_VERIFICATION}'))
    status, mensagens = mail.search(None, f'SINCE {LAST_VERIFICATION}')
    print(status, mensagens)
    if status != 'OK':
        print("Erro ao buscar emails.")
        return
    
    email_ID = mensagens[0].split()
    print(email_ID)
    print(f"Total de emails: {len(email_ID)}\n")

    for unique_ID in email_ID: #LOOP QUE TRATA CADA ID (EMAIL UNICO) INDIVIDUALMENTE
        status, dados = mail.fetch(unique_ID, '(RFC822)')
        if status != 'OK':
            print(f"Erro ao buscar email {unique_ID.decode()}")
            continue
        raw_Email = dados[0][1] #EMAIL RAW (DADOS E MENSAGEM)
        msg_Email = email.message_from_bytes(raw_Email) # MENSAGEM
        subject, encoding = decode_header(msg_Email["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8", errors="ignore")

        emailDictChanger["id"]= unique_ID.decode()
        emailDictChanger["sender"] = msg_Email["From"]
        emailDictChanger["date"] = msg_Email["Date"]
        emailDictChanger["subject"] = subject
        
        for part in msg_Email.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            filename = part.get_filename()

            # ======== Corpo em texto simples ========
            if content_type == "text/plain" and not filename:
                try:
                    emailDictChanger["body"] = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="ignore"
                    )
                except Exception:
                    emailDictChanger["body"] = ""

            # ======== Corpo HTML ========
            elif content_type == "text/html" and not filename:
                try:
                    emailDictChanger["body_Html"] = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="ignore"
                    )
                except Exception:
                    emailDictChanger["body_Html"] = ""

            # ======== Anexo (attachment ou inline com filename) ========
            elif filename:
                emailDictChanger["has_Attachment"] = True

                # Decodificar nome, se necessário
                fname, enc = decode_header(filename)[0]
                if isinstance(fname, bytes):
                    fname = fname.decode(enc or "utf-8", errors="ignore")

                # Caminho completo para salvar o arquivo
                filepath = os.path.join(PASTA_ANEXOS, fname)

                # Evita sobrescrever arquivos com o mesmo nome
                if os.path.exists(filepath):
                    base, ext = os.path.splitext(fname)
                    filepath = os.path.join(PASTA_ANEXOS, f"{base}_{unique_ID.decode()}{ext}")

                # Salva o anexo
                payload = part.get_payload(decode=True)
                if payload:
                    with open(filepath, "wb") as f:
                        f.write(payload)
                    print(f"✅ Anexo salvo: {filepath}")
                    emailDictChanger["attachments"].append(fname)
        date_Email = msg_Email["Date"]
        sender_Email = msg_Email["From"]
        emails_List.append(emailDictChanger)
        emailDictChanger = emailDict.copy()

def link_Parser(content_List):
    for content_item in content_List:
        body_text = content_item.get("body", "")
        
        # Expressão regular para capturar links (http e https)
        links = re.findall(r'https?://[^\s\'"<>]+', body_text)

        """print(f"ID: {email_item['id']} — Total de links encontrados: {len(links)}")
        for link in links:
            print(link)
        print("-" * 80)"""
        content_item["links"] = links

def sha256_File(filepath, chunk_size=8192):
    """Retorna o hash SHA-256 em hexadecimal para o arquivo informado."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

mail.select("inbox")
print_assuntos_emails(mail)
link_Parser(emails_List)