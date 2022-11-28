FROM golang:1.19-alpine

WORKDIR /web

COPY . .

RUN apk update && \
    apk upgrade && \
    rm -rf /var/cache/apk/*

RUN go build

ENTRYPOINT [ "./web" ]