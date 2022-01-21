FROM golang:1.17.6-buster

WORKDIR /web

COPY . .

RUN go build .

ENTRYPOINT [ "./web" ]