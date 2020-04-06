import sys
import smtplib
import config
import socket
import socks
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from logsjsonparser import parse_logs_json

if len(sys.argv) != 2:
    Exception("a filename must be given")

filename = sys.argv[1]

# aquivo de logsjasonparser
body = parse_logs_json(filename)

dia_hora = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")

msg = MIMEMultipart()
msg['From'] = config.FROM_EMAIL
msg['To'] = config.TO_EMAIL
msg['Subject'] = 'Erros de execução de testes no dia ' + dia_hora

msg.attach(MIMEText(body, 'plain'))

server = smtplib.SMTP('smtp.globoi.com', 25)
try:
    text = msg.as_string()
    server.sendmail(config.FROM_EMAIL, config.TO_EMAIL, text)
    print('E-mail enviado em '+ dia_hora)
except Exception as e:
    print(e)
finally:
    server.quit()