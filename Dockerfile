FROM python:3.11

WORKDIR /app
COPY src/ /app
RUN pip install -r requirements.txt

EXPOSE 8001
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]