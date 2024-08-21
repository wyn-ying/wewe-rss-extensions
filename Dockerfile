FROM python:3.11-slim AS extensions

WORKDIR /app

COPY . .

ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install -r requirements.txt

ENV ENABLE_NOTIFIER="1" \
    DATABASE_URL="file:../data/wewe-rss.db" \
    DATABASE_TYPE="sqlite" \
    NOTIFY_INTERVAL_MINUTES=240 \
    ENABLE_CRON="1" \
    WEWERSS_ORIGIN_URL="http://127.0.0.1:4000" \
    CONF_PATH=/app/data/conf/conf.yaml

RUN chmod +x ./entrypoint.sh
EXPOSE 4100
ENTRYPOINT ["./entrypoint.sh"]
