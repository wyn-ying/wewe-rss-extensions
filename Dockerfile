FROM python:3.11-slim AS extensions

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENV DATABASE_URL="file:../data/wewe-rss.db" \
    DATABASE_TYPE="sqlite" \
    NOTIFY_INTERVAL_MINUTES=240 \
    CONF_PATH=/app/data/conf/conf.yaml

RUN chmod +x ./entrypoint.sh
EXPOSE 4100
ENTRYPOINT ["./entrypoint.sh"]
