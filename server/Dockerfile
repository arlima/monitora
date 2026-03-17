FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py bot.py start.sh ./
RUN chmod +x start.sh

RUN mkdir -p /app/data

EXPOSE 1234

CMD ["./start.sh"]
