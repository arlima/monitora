# Monitora - Sistema simples de monitoração #

Desenvolvi este sistema para ter uma maneira simples de saber se algumas máquinas de casa estavam conseguindo se comunicar adequadamente com um servidor remoto na AWS. Isto serve para saber se as máquinas estão ativas, se a conexão delas com a internet está ok e até mesmo se a internet de casa está funcionando.

Como instalar e configurar ?

Parte 1: Endpoint (endpoint.py e endpoint.yml)

- Instalar no dispositivo que você quer monitorar se está conseguindo se comunicar com um servidor remoto (AWS, Azure, etc).
- O arquivo endpoint.py deve ser instalado na pasta monitora no /home do usuário que vai rodar o programa.
- O arquivo endpoint.yml deve ser instalado no /etc/monitora/ do servidor que vai rodar o programa. Nele existem várias configurações importantes que precisam ser ajustadas.
- Rodar o arquivo endpoint.py e mantê-lo ativo.

Parte 2: Servidor de API (server.py e server.yml)

- Instalar no servidor remoto (AWS, Azure, etc). No meu caso, está instalado em um servidor lightsail da AWS com serviço de ip fixo e a porta 1234 aberta.
- O arquivo server.py deve ser instalado na pasta monitora no /home do usuário que vai rodar o programa. Este programa sobe um servidor na porta 1234 que recebe informações dos diversos endpoints.
- O arquivo server.yml deve ser instalado no /etc/monitora/ do servidor remoto. Nele existem várias configurações importantes que precisam ser ajustadas.
- Rodar o arquivo server.py e mantê-lo ativo.

Parte 3: Bot (bot.py e bot.yml)
- Instalar no servidor mesmo servidor remoto que o servidor de API.
- O arquivo bot.py deve ser instalado na pasta monitora no /home do usuário que vai rodar o programa. Este programa é um bot de telegram com o qual um usuário pode se comunicar. Se o usuário enviar o comando /status para ele, a resposta será o status do server e quando foi a última vez que cada host mandou um sinal.
- Este programa também verifica se os endpoints estão enviando os sinais periodicamente. Caso não estejam, ele envia uma mensagem para o grupo de telegram configurado
- O arquivo bot.yml deve ser instalado no /etc/monitora/ do servidor remoto. Nele existem várias configurações importantes que precisam ser ajustadas.
- Somente comandos enviados no grupo configurado no arquivo bot.yml são respondidos pelo bot.
- Rodar o arquivo bot.py e mantê-lo ativo.

O que são os arquivos .host

- O sistema de monitoração não usa nenhum banco de dados. Os arquivos .host são criados pelo Servidor de API e lidos pelo Bot. Cada arquivo corresponde a um endpoint e contém o timestamp da última vez que o endpoint se comunicou com o servidor remoto (API).

Como testar ?

- Pare o programa endpoint.py de um dos hosts que estão sendo monitorados. Você deve receber uma mensagem no grupo de telegram configurado dizendo que ele está com problemas de comunicação.
- Ative o programa endpoint.py do host novamente e você deve receber uma mensagem dizendo que ele voltou ao normal.

Como executar os arquivos .py ?
- Eu coloquei todos os arquivos .py como serviços no 
linux. Mais informações sobre como fazer isso podem ser obtidas no artigo: https://medium.com/codex/setup-a-python-script-as-a-service-through-systemctl-systemd-f0cc55a42267
- Na pasta systemctl estão os arquivos de configuração que utilizei.

Como obter o TOKEN do telegram ou o ID do grupo para onde enviar as mensagens ?
- Veja mais informações aqui: https://blog.gabrf.com/posts/HowToBot/
