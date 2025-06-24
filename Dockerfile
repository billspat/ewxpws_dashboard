FROM python:3.11

ENV PORT=5006

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
 python3 -m pip install --no-cache-dir --upgrade -r /app/requirements.txt 

COPY . /app

RUN mkdir /.cache && chmod 777 /.cache

# TODO use the correct command
CMD ["python", "app.py"]


