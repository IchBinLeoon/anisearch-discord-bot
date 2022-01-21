FROM python:3.10.1-buster

WORKDIR /asuka

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "asuka.py" ]