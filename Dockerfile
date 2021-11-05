# FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

WORKDIR /app/

COPY ./requirements.txt /app/

RUN pip install -r requirements.txt

COPY ./api /app
ENV PYTHONPATH=/app
