FROM alpine:latest

# Установим необходимые утилиты
RUN apk add --no-cache util-linux

# Создадим директории
RUN mkdir -p /app /data

# Копируем скрипт
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

WORKDIR /data

# Устанавливаем точку входа
ENTRYPOINT ["/app/entrypoint.sh"]