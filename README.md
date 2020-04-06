# README

## Executar os testes

- Execurtar o arquivo <i>./crontab.sh </i>no terminal para rodar as features
- No <i>./crontab.sh </i> temos as chamadas para execução do behave que lê as features e após sua execução se houver erro, dispara um e-mail.

## Python

- Instalar python na maquina, versão 3.8
- Instalar py.test `pip install pytest`
    
- Criar as features com nomeclatura test_ + `arquivo.py`

- Usar `py.test` no terminal para acompanha a execução na headspin
- pip install pytest

- Executar `py.test - v` para todos os arquivos dentro do diretório headspin

- Executar `py.test -v android/` + nome do arquivo para os arquivos Android

- Executar `py.test -v ios/` + nome do arquivo para os arquivos IOS


## Docker

### Criando maquina docker
- docker-machine create ou docker-machine create default
- docker-machine create nome+da+maquina

### Lista itens do Docker
- docker-machine

### Lista itens dentro do Docker
- docker ps ou docker container ls
- docker ps -a

### Renomear imagem 
- docker rename id-container nome-novo

### Verifica iP 
- docker-machine ip default

### Criar container em uma pasta: 
- `docker run -v $PWD:/src -it headspin bash `

<!-- ### Remover container: 
- `docker run -v $PWD:/src -it headspin bash ` -->

### Criar pasta SRC para executar comandos
- cd src/
- Executar linha de comando

### Abrindo o mesmo container
- docker start -ai container_id
- docker start -ai 8d97e6e9f1fc

### Lista intens no Docker
- pip freeze

### Passando porta para o docker se comunicar com Appium
- `docker run -p 4723:4723  -v $PWD:/src -it headspin bash `

### ADB para listar device
- `adb devices -l`
- /Users/diretorio-users/Library/Android/sdk/platform-tools/adb devices -l

### Debug Pytest Debug
- instalar pip install ipdb
- adicionar o `import ipdb` no arquivo inc
- adicionar essa chamada `ipdb.set_trace()` no ponto onde precisa executar debug 
- Clicar `c` no terminal para dar continuidade a execução
- Clicar `n` no terminal para pular os passos do Debug

## Arquivo Headspin
`python` + `nome-do-arquivo` + `ID do telefone` + `URL`  
 <i> python globo_continue_assista_102319.py</i> + `0057160804` +  ` https://br-sao.headspin.io:7012/v0/70b466e0d69848c48a992268a95177ad/wd/hub`

### Url padrão Headspin pra executar no terminal comum
python globo_continue_assista_102319_Di.py 0057160804 <i>https://br-sao.headspin.io:7012/v0/4759afddaf134367b5c7b110bd50610e/wd/hub</i>