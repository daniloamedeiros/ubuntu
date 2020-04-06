import datetime
from time import sleep

while 1 != 2:
    sleep(5)
    horaAtual = datetime.datetime.now().strftime('%H:%M:%S')
    print("execução às: ", horaAtual)

else:
    print('após iteração')