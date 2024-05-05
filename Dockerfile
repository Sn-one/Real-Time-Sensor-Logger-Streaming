FROM python:3.8-slim
WORKDIR /app
COPY . /app
RUN pip install Flask kafka-python
EXPOSE 5000
CMD ["python", "./server.py"]
