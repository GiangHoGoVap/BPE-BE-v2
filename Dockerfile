FROM python:3.11-slim as bpsky-be-image

WORKDIR /bpe

COPY requirements.txt .

RUN pip install -r ./requirements.txt

RUN pip install gunicorn

COPY . .

CMD gunicorn --worker-class eventlet --workers 1 --bind 0.0.0.0:${PORT:-8000} run:bpsky