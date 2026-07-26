FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# because i use free plan of render, there is no shell(SSH) option so we run migration here.
CMD alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000