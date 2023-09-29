FROM python:3.9.11
WORKDIR /app
COPY . /app
EXPOSE 80
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "app.py"]