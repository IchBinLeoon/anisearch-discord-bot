FROM golang:1.16.6-buster

WORKDIR /web

COPY . .

RUN go build .

ENTRYPOINT [ "./web" ]