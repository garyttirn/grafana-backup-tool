# ---------- Build stage ----------
FROM alpine:latest AS builder

RUN echo "@edge http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
    && apk --no-cache add python3-dev libffi-dev gcc libc-dev py3-pip py3-cffi py3-cryptography ca-certificates bash

WORKDIR /opt/grafana-backup-tool
ADD . /opt/grafana-backup-tool

# Create venv and install dependencies
RUN python3 -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --no-cache-dir .

# ---------- Final stage ----------
FROM alpine:latest

LABEL maintainer="ysde108@gmail.com"

ENV RESTORE=false
ENV ARCHIVE_FILE=""

RUN echo "@edge http://dl-cdn.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
    && apk --no-cache add python3 py3-pip ca-certificates bash \
    && rm -rf /var/cache/apk/*

# Copy only the venv and tool from builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /opt/grafana-backup-tool /opt/grafana-backup-tool

WORKDIR /opt/grafana-backup-tool

# Permissions
RUN chmod -R a+r /opt/grafana-backup-tool \
 && find /opt/grafana-backup-tool -type d -print0 | xargs -0 chmod a+rx \
 && chown -R 1337:1337 /opt/grafana-backup-tool

USER 1337

ENV PATH="/opt/venv/bin:$PATH:/opt/grafana-backup-tool"

CMD sh -c 'if [ "$RESTORE" = true ]; then \
              if [ ! -z "$AWS_S3_BUCKET_NAME" ] || [ ! -z "$AZURE_STORAGE_CONTAINER_NAME" ] || [ ! -z "$GCS_BUCKET_NAME" ]; then \
                grafana-backup restore $ARCHIVE_FILE; \
              else \
                grafana-backup restore _OUTPUT_/$ARCHIVE_FILE; \
              fi; \
            else \
              grafana-backup save; \
            fi'
