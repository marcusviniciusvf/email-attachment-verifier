import imaplib
import email
from email.header import decode_header
import os
import json

with open("email_user.json") as f: #ABRIR O JSON COM INFORMAÇÕES DE LOGIN E SENHA DO EMAIL
    config = json.load(f)

IMAP_SERVER = "imap.gmail.com" #CABEÇALHO DE LOGIN IMAP
EMAIL_USER = config["EMAIL_USER"]
EMAIL_PASS = config["EMAIL_PASS"]


PASTA_ANEXOS = "downloaded_Files"
os.makedirs(PASTA_ANEXOS, exist_ok=True)

mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL_USER, EMAIL_PASS)

mail.select("inbox")

status, mensagens = mail.search(None, 'ALL')
ids = mensagens[0].split()

for item in ids:
    status, mensagens = mail.fetch(item, '(RFC822)')
    #print('Message %s\n%s\n' % (item, mensagens[0][1]))

raw_email = mensagens[0][1]
msg = email.message_from_bytes(raw_email)
subject, encoding = decode_header(msg["Subject"])[0]
if isinstance(subject, bytes):
    subject = subject.decode(encoding or "utf-8")

print(f'Message {item.decode()} - Subject: {subject}')
print(ids)
print("-"*30)
print(mensagens[0])
print("-"*30)
print(mensagens)

