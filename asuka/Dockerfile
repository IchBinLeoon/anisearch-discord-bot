FROM python:3.10-alpine

WORKDIR /asuka

COPY . .

RUN apk update && \
    apk upgrade && \
    rm -rf /var/cache/apk/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

CMD [ "python", "asuka.py" ]