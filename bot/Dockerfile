FROM python:3.12-alpine3.20
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

RUN pip install pip --upgrade
COPY requirements.txt .
RUN pip install -r requirements.txt

# pg_dump / psql for /backup and /restore admin commands.
# Pinned to postgresql16-client to match the `postgres:16` server —
# newer pg_dump emits SET transaction_timeout (PG17+) which PG16 rejects.
# Alpine 3.20 is the last release whose default postgresql-client is 16.
RUN apk add --no-cache postgresql16-client

# Always prefer IPv4.
RUN echo "precedence ::ffff:0:0/96  100" >> /etc/gai.conf

RUN echo "net.ipv6.conf.all.disable_ipv6=1" >> /etc/sysctl.conf
RUN echo "net.ipv6.conf.default.disable_ipv6=1" >> /etc/sysctl.conf


COPY . ./bot

CMD [ "python", "-m", "bot"]
