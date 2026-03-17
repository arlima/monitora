# Monitora

A simple monitoring system to check if machines are alive and able to communicate with a remote server. When an endpoint stops sending signals, an alert is sent to a Telegram group.

## Architecture

The system is split into two components, each running on its own machine:

- **server** — runs on the remote server (AWS, Azure, etc). Contains the API server that receives signals from endpoints and the Telegram bot that sends alerts.
- **endpoint** — runs on each machine you want to monitor. Sends periodic signals to the server.

Communication between them is done via HTTP on port `8123`.

## How it works

1. Each endpoint sends an HTTP POST signal to the server every `INTERVAL` seconds.
2. The server records the timestamp of the last received signal in a `.host` file per endpoint, inside the `server/data/` folder.
3. The bot checks every `INTERVAL_CHECKER` seconds if endpoints are sending signals, discovering hosts automatically from existing `.host` files. If an endpoint goes more than `INTERVAL_PROBLEM` seconds without sending a signal, an alert is sent to the Telegram group. When the endpoint recovers, a recovery message is sent.

## Project structure

```
monitora/
├── server/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   ├── server.py
│   ├── bot.py
│   ├── start.sh
│   ├── data/                   # .host files — ignored by git
│   ├── monitora.yml            # ignored by git — create from .example
│   └── monitora.yml.example
└── endpoint/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── requirements.txt
    ├── endpoint.py
    ├── endpoint.yml            # ignored by git — create from .example
    └── endpoint.yml.example
```

## Installation

### Server

```bash
cd server
cp monitora.yml.example monitora.yml
```

Edit `monitora.yml` with your settings, then start the container:

```bash
docker compose up -d
```

### Endpoint

```bash
cd endpoint
cp endpoint.yml.example endpoint.yml
```

Edit `endpoint.yml` with the server address and credentials, then start the container:

```bash
docker compose up -d
```

## Configuration

### monitora.yml

| Key | Description |
|-----|-------------|
| `PATH` | Directory where `.host` files will be stored. Do not change. |
| `PORT` | API server port |
| `USER` | Username for API authentication |
| `PWD`  | Password for API authentication |
| `TOKEN` | Telegram bot token |
| `CHATID` | Telegram group ID to send messages to |
| `INTERVAL_CHECKER` | Interval in seconds between each endpoint check by the bot |
| `INTERVAL_READ` | Interval in seconds to read the signals |
| `INTERVAL_PROBLEM` | Time in seconds without a signal before considering a problem |
| `INTERVAL_RETRY_MESSAGE` | Interval in seconds between retry alert messages |

### endpoint.yml

| Key | Description |
|-----|-------------|
| `SERVER` | Full server URL, e.g. `http://YOUR_IP:8123/signal` |
| `HOST` | Endpoint name |
| `USER` | Username for API authentication |
| `PWD`  | Password for API authentication |
| `INTERVAL` | Interval in seconds between signal sends |

## Managing monitored hosts

Hosts are discovered automatically from `.host` files in the `server/data/` folder. No additional configuration is needed to add a new host — the endpoint just needs to start sending signals.

To stop monitoring a host, delete the corresponding file:

```bash
rm server/data/hostname.host
```

## Bot commands

Only messages sent in the group configured in `CHATID` are accepted.

| Command | Description |
|---------|-------------|
| `/status` | Shows the server status and time since the last signal from each endpoint |
| `/restart` | Restarts the API server process |

## How to get the Telegram TOKEN and CHATID

See: https://blog.gabrf.com/posts/HowToBot/
