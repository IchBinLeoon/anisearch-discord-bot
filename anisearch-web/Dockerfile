FROM rust:1.88-alpine3.22 AS builder

WORKDIR /app

RUN apk add --no-cache musl-dev protobuf

COPY . .

RUN cargo build --release --bin anisearch-web

FROM alpine:3.22

RUN apk add --no-cache curl

COPY --from=builder /app/target/release/anisearch-web /usr/local/bin/anisearch-web

HEALTHCHECK --interval=1m --timeout=3s --start-period=10s --retries=1 \
    CMD curl -fsS http://localhost:8080/api/health || exit 1

EXPOSE 8080

ENTRYPOINT ["anisearch-web"]
