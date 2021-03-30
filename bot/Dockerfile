FROM python:3.8.6-buster

WORKDIR /bot

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-m", "anisearch" ]