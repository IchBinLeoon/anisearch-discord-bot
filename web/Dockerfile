FROM golang:1.17.5-buster

WORKDIR /web

COPY . .

RUN go build .

ENTRYPOINT [ "./web" ]