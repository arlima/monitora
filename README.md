# Monitora - Sistema simples de monitoração #

Desenvolvi este sistema para ter uma maneira simples de saber se algumas máquinas de casa estavam conseguindo se comunicar adequadamente com um servidor remoto na AWS. Isto serve para saber se as máquinas estão ativas, se a conexão delas com a internet está ok e até mesmo se a internet de casa está funcionando.

Como instalar e configurar ?

Parte 1: Endpoint (endpoint.py e endpoint.yml)

Instalar no dispositivo que você quer monitorar se está conseguindo se comunicar com um servidor remoto (AWS, Azure, etc).
O arquivo endpoint.py deve ser instalado na pasta monitora no /home do usuário que vai rodar o programa.
O arquivo endpoint.yml deve ser instalado no /etc/monitora/ do servidor que vai rodar o programa. Nele existem várias configurações importantes que precisam ser ajustadas.
Rodar o arquivo endpoint.py

Parte 2: Servidor de API (monitora.py e monitora.yml)

Instalar no servidor remoto (AWS, Azure, etc)
O arquivo monitora.py deve ser instalado na pasta monitora no /home do usuário que vai rodar o programa. Este programa sobe um servidor na porta 1234 que recebe informações dos diversos endpoints.
O arquivo monitora.yml deve ser instalado no /etc/monitora/ do servidor remoto. Nele existem várias configurações importantes que precisam ser ajustadas.
Rodar o arquivo monitora.py

Parte 3: Bot (bot.py e bot.yml)

Instalar no servidor mesmo servidor remoto que o servidor de API.
O arquivo bot.py deve ser instalado na pasta monitora no /home do usuário que vai rodar o programa. Este programa monitora os dados recebidos dos endpoints e notifica um grupo de telegram caso algum deles não esteja se comunicando com o Servidor de API.
O arquivo bot.yml deve ser instalado no /etc/monitora/ do servidor remoto. Nele existem várias configurações importantes que precisam ser ajustadas.
Rodar o arquivo bot.py

O que sãpo os arquivos .host

O sistema de monitoração não usa nenhum banco de dados. Os arquivos .host são criados pelo Servidor de API e lidos pelo Bot. Cada arquivo corresponde a um endpoint e contém o timestamp da última vez que o endpoint se comunicou com o servidor remoto (API).

Como testar ?

Pare o programa endpoint.py de um dos hosts que estão sendo monitorados. Você deve receber uma mensagem no grupo de telegram configurado dizendo que ele está com problemas de comunicação.
Ative o programa endpoint.py do host novamente e você deve receber uma mensagem dizendo que ele voltou ao normal.
