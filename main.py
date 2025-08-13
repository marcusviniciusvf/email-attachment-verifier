import imaplib
import email
from email.header import decode_header
import os
import json
from datetime import datetime

with open("configs.json") as f: #ABRIR O JSON COM INFORMAÇÕES DE LOGIN E SENHA DO EMAIL
    config_Data = json.load(f)

IMAP_SERVER = "imap.gmail.com" #CABEÇALHO DE LOGIN IMAP
EMAIL_USER = config_Data["EMAIL_USER"]
EMAIL_PASS = config_Data["EMAIL_PASS"]
LAST_VERIFICATION = config_Data["LAST_VERIFICATION"]
DATE_TODAY = (datetime.now()).strftime("%d-%b-%Y")

emailDict = {
    "id": None,              # ID UNICO IMAP
    "date": None,            # DATA
    "sender": None,          # REMETENTE
    "subject": None,         # ASSUNTO
    "body": None,            # CORPO EMAIL
    "body_Html": None,       # CORPO HTML
    "has_Attachment": False, # TEM ANEXO
    "attachments": []        # LISTA DE ANEXOS
}
emailDictChanger = emailDict
emails = []

PASTA_ANEXOS = "downloaded_Files"
os.makedirs(PASTA_ANEXOS, exist_ok=True)
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL_USER, EMAIL_PASS)

print(f'SINCE {LAST_VERIFICATION}')
print(type(f'SINCE {LAST_VERIFICATION}'))
print(LAST_VERIFICATION)

def print_assuntos_emails(mail):
    # Buscar todos os e-mails
    print('SINCE {LAST_VERIFICATION}')
    print(type('SINCE {LAST_VERIFICATION}'))
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
        
        raw_email = dados[0][1] #EMAIL RAW (DADOS E MENSAGEM)
        msg = email.message_from_bytes(raw_email) # MENSAGEM
        print(msg)
        subject, encoding = decode_header(msg["Subject"])[0]
        print(subject)
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8", errors="ignore")
        
        print(f"Email ID {unique_ID.decode()}: Assunto: {subject}")
    




mail.select("inbox")

print_assuntos_emails(mail)


