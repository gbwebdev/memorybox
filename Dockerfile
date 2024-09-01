FROM debian:bookworm-slim

ENV RUN_MODE=prod \
    GUNICORN_WORKERS=2 \
    GUNICORN_PORT=8000 \
    GUNICORN_TIMEOUT=30

RUN adduser --disabled-password -comment "" memorybox
COPY install.sh /home/memorybox/
COPY --chown=memorybox:memorybox pymemorybox /home/memorybox/pymemorybox
COPY --chown=memorybox:memorybox .git /home/memorybox/.git
COPY entrypoint.sh /entrypoint.sh

WORKDIR /home/memorybox

RUN export SUDO_UID=$(id -u memorybox) \
 && export SUDO_USER=memorybox \
 && ./install.sh \
 && rm -rf /home/memorybox/.git \
 && echo "source ~/venv/bin/activate" >> /home/memorybox/.bashrc

USER memorybox

ENTRYPOINT '/entrypoint.sh'