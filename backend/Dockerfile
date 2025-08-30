FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

# Set working directory to /app/src where main.py is located
WORKDIR /app/src

EXPOSE 5000

CMD ["python", "main.py"]
