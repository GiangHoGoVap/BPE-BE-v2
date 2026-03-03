FROM python:3.11-slim as bpsky-be-image

WORKDIR /bpe

COPY requirements.txt .

RUN pip install -r ./requirements.txt

RUN pip install gunicorn

COPY . .

CMD gunicorn --bind 0.0.0.0:8000 run:bpsky