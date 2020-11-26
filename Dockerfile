FROM python:3.8.6-buster

WORKDIR /AnimeSearch

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-m", "animesearch" ]