import imaplib
import email
from email.header import decode_header
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import re
import hashlib 
import requests
from functools import reduce

IMAP_SERVER = os.getenv('IMAP_SERVER')
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
LAST_VERIFICATION = os.getenv('LAST_VERIFICATION')
VIRUSTOTAL_APIKEY= os.getenv('VIRUSTOTAL_APIKEY')
DATE_TODAY = (datetime.now()).strftime("%d-%b-%Y")
load_dotenv()

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
analyzed_Emails = []

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
        content_item["links"] = links

def sha256_File(path_File, chunk_size=8192):
    h = hashlib.sha256()
    with open(f'downloaded_Files/{path_File}', "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()

def checkSha256(filename):
    url = f"https://www.virustotal.com/api/v3/files/{filename}"

    headers = {
        "accept": "application/json",
        "x-apikey": VIRUSTOTAL_APIKEY
    }
    try:
        response = requests.get(url, headers=headers)
         # Checa o status code
        if response.status_code == 200:
            # Tudo certo, retorna o JSON
            return response.json()
        else:
            print(f"Erro {response.status_code}: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        # Captura erros de rede
        print(f"Erro de requisição: {e}")
        return None
    
mail.select("inbox")
print_assuntos_emails(mail)
link_Parser(emails_List)

for item in emails_List: #Reads each individual e-mail response
    if item["has_Attachment"]== True:
        for i in range(len(item['attachments'])): #Go through attachments
            analysis_Response = checkSha256(sha256_File(item['attachments'][i-1]))
            if type(analysis_Response)==dict:
                attributes = analysis_Response["data"]
                keys_needed = [
                    ['links'],
                    ["attributes", "sha256"],
                    ["attributes", "last_analysis_stats"],
                    ["attributes", "sandbox_verdicts"]
                ]
                filtered_dynamic = {
                    path[-1]: reduce(lambda acc, key: acc.get(key, {}) if isinstance(acc, dict) else None, path, attributes)
                    for path in keys_needed
                }

