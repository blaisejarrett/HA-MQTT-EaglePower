FROM python:3
COPY requirements.txt /app/
COPY server.py /app/
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 44202
ENTRYPOINT ["python", "server.py"]