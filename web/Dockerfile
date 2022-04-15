FROM golang:1.18-alpine

WORKDIR /web

COPY . .

RUN apk update && \
    apk upgrade && \
    rm -rf /var/cache/apk/*

RUN go build

ENTRYPOINT [ "./web" ]