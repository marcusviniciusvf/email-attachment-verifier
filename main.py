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
    print('SINCE f{LAST_VERIFICATION}')
    print(type('SINCE f{LAST_VERIFICATION}'))
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
            content_disposition = part.get_content_disposition() 
            if content_type == "text/plain":# Corpo em texto
                emailDictChanger["body"] = part.get_payload(decode=True).decode('utf-8', errors='ignore')

            elif content_type == "text/html":# Corpo em HTML
                emailDictChanger["body_Html"] = 'test'#part.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            elif content_disposition == "attachment":# Anexos
                emailDictChanger["has_Attachment"] = True
                filename = part.get_filename()
                if filename:
                    # decodificando nome do arquivo se necessário
                    fname, enc = decode_header(filename)[0]
                    if isinstance(fname, bytes):
                        fname = fname.decode(enc or "utf-8", errors="ignore")
                        emailDictChanger["attachments"].append(fname)
        date_Email = msg_Email["Date"]
        sender_Email = msg_Email["From"]
        emails_List.append(emailDictChanger)
        emailDictChanger = emailDict.copy()

mail.select("inbox")

print_assuntos_emails(mail)


