FROM golang:1.17.1-buster

WORKDIR /web

COPY . .

RUN go build .

ENTRYPOINT [ "./web" ]