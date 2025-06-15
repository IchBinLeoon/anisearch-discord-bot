FROM rust:1.87-alpine AS builder

WORKDIR /app

RUN apk add --no-cache musl-dev

COPY . .

RUN cargo build --release --bin anisearch-web

FROM alpine:3.22

COPY --from=builder /app/target/release/anisearch-web /usr/local/bin/anisearch-web

EXPOSE 8080

ENTRYPOINT ["anisearch-web"]
