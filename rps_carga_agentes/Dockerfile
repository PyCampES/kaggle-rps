FROM python:3.7


COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

ENV FILES /files

EXPOSE 80

COPY ./app /app

RUN mkdir $FILES

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]



