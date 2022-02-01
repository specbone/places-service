FROM python:3.9-buster
ADD . /code
WORKDIR /code
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt
CMD python3 app.py