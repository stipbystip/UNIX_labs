FROM alpine:latest


RUN apk add --no-cache bash flock coreutils


COPY container_script.sh /container_script.sh


RUN chmod +x /container_script.sh


CMD ["/container_script.sh"]