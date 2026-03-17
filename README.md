# Monitora

A simple monitoring system to check if machines are alive and able to communicate with a remote server. When an endpoint stops sending signals, an alert is sent to a Telegram group.

## Architecture

The system is split into two components, each running on its own machine:

- **server** — runs on the remote server (AWS, Azure, etc). Contains the API server that receives signals from endpoints and the Telegram bot that sends alerts.
- **endpoint** — runs on each machine you want to monitor. Sends periodic signals to the server.

Communication between them is done via HTTP on port `8123`.

## How it works

1. Each endpoint sends an HTTP POST signal to the server every `INTERVAL` seconds.
2. The server records the timestamp of the last received signal in a SQLite database (`server/data/monitora.db`).
3. The bot checks every `INTERVAL_CHECKER` seconds if endpoints are sending signals. If an endpoint goes more than `INTERVAL_PROBLEM` seconds without sending a signal, an alert is sent to the Telegram group. When the endpoint recovers, a recovery message is sent.

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
│   ├── data/                   # SQLite database — ignored by git
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
docker compose up -d --build
```

### Endpoint

```bash
cd endpoint
cp endpoint.yml.example endpoint.yml
```

Edit `endpoint.yml` with the server address and credentials, then start the container:

```bash
docker compose up -d --build
```

## Configuration

### monitora.yml

| Key | Description |
|-----|-------------|
| `PATH` | Directory where the database will be stored. Do not change. |
| `PORT` | API server port |
| `USER` | Username for API authentication |
| `PWD` | Password for API authentication |
| `TOKEN` | Telegram bot token |
| `CHATID` | Telegram group ID to send messages to |
| `INTERVAL_CHECKER` | Interval in seconds between each endpoint check by the bot |
| `INTERVAL_PROBLEM` | Time in seconds without a signal before considering a problem |
| `INTERVAL_RETRY_MESSAGE` | Interval in seconds between retry alert messages |

### endpoint.yml

| Key | Description |
|-----|-------------|
| `SERVER` | Full server URL, e.g. `http://YOUR_IP:8123/signal` |
| `HOST` | Endpoint name (alphanumeric, `-` and `_` only) |
| `USER` | Username for API authentication |
| `PWD` | Password for API authentication |
| `INTERVAL` | Interval in seconds between signal sends |

## Managing monitored hosts

Hosts are registered automatically when they first send a signal — no additional configuration needed.

To stop monitoring a host, use the bot command:

```
/remove_host hostname
```

## Bot commands

Only messages sent in the group configured in `CHATID` are accepted.

| Command | Description |
|---------|-------------|
| `/status` | Shows the server status and time since the last signal from each endpoint |
| `/restart` | Restarts the API server process |
| `/remove_host <hostname>` | Removes a host from monitoring |

## Changing the default port (8123)

To use a different port, update it in four places:

**On the server machine:**

1. **`server/monitora.yml`** — set `PORT` to the new value:
   ```yaml
   PORT: 9000
   ```

2. **`server/Dockerfile`** — update the `EXPOSE` directive:
   ```dockerfile
   EXPOSE 9000
   ```

3. **`server/docker-compose.yml`** — update the port mapping to match:
   ```yaml
   ports:
     - "9000:9000"
   ```

   After updating these three files, rebuild and restart the server container:

   ```bash
   cd server
   docker compose up -d --build
   ```

**On each endpoint machine:**

4. **`endpoint/endpoint.yml`** — update the port in the `SERVER` URL:
   ```yaml
   SERVER: "http://YOUR_IP:9000/signal"
   ```

   The endpoint `docker-compose.yml` does not need to be changed — the endpoint only makes outbound HTTP requests to the server and does not expose any port itself.

   After editing `endpoint.yml`, restart the endpoint container:

   ```bash
   cd endpoint
   docker compose up -d --build
   ```

## How to get the Telegram TOKEN and CHATID

See: https://blog.gabrf.com/posts/HowToBot/
