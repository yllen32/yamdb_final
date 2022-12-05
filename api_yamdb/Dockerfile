FROM python:3.7.15-slim
WORKDIR /infra
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000"]