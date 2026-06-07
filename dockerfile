FROM python:3.9-slim
WORKDIR /app
COPY . .
ENTRYPOINT [ "python" , "main.py" ]
