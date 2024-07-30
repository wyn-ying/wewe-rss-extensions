FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENV ENABLE_NOTIFIER=1
ENV DATABASE_URL="file:../data/wewe-rss.db" \
    DATABASE_TYPE="sqlite" \
    NOTIFY_INTERVAL_MINUTES=240 \
    NOTIFIER_CONF_PATH=/app/data/conf/notify.yaml

RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
