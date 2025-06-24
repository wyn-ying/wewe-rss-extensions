FROM python:3.11-slim AS extensions

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENV ENABLE_NOTIFIER="1" \
    DATABASE_URL="mysql://root:123456@127.0.0.1:3306/gzhweb" \
    DATABASE_TYPE="zlz" \
    NOTIFY_INTERVAL_MINUTES=240 \
    ENABLE_CRON="1" \
    CONF_PATH=/app/data/conf/conf.yaml

RUN chmod +x ./entrypoint.sh
EXPOSE 4100
ENTRYPOINT ["./entrypoint.sh"]
