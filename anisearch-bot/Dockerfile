FROM rust:1.87-alpine AS builder

WORKDIR /app

RUN apk add --no-cache musl-dev protobuf

COPY . .

RUN cargo build --release --bin anisearch-bot

FROM alpine:3.22

ARG TARGETOS
ARG TARGETARCH
ARG GRPC_HEALTH_PROBE_VERSION=v0.4.38

RUN apk add --no-cache curl

RUN curl -fsSL -o /usr/local/bin/grpc_health_probe \
        https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-${TARGETOS}-${TARGETARCH} && \
    chmod +x /usr/local/bin/grpc_health_probe

COPY --from=builder /app/target/release/anisearch-bot /usr/local/bin/anisearch-bot

HEALTHCHECK --interval=1m --timeout=3s --start-period=10s --retries=1 \
    CMD grpc_health_probe -addr=localhost:50051 || exit 1

EXPOSE 50051

ENTRYPOINT ["anisearch-bot"]
