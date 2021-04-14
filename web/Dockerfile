FROM golang:1.16.3-buster

WORKDIR /web

COPY . .

RUN go build .

ENTRYPOINT [ "./main" ]