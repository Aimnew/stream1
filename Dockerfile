FROM python:3.9-slim

WORKDIR /stream1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requierements.txt

COPY . .

CMD ["streamlit", "run", "app.py"]
