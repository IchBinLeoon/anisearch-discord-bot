FROM golang:1.16.2-buster

WORKDIR /web

COPY . .

RUN go build .

ENTRYPOINT [ "./main" ]