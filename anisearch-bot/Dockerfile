FROM rust:1.87-alpine AS builder

WORKDIR /app

RUN apk add --no-cache musl-dev

COPY . .

RUN cargo build --release --bin anisearch-bot

FROM alpine:3.22

COPY --from=builder /app/target/release/anisearch-bot /usr/local/bin/anisearch-bot

ENTRYPOINT ["anisearch-bot"]
