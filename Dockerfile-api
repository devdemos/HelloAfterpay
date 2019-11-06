FROM python:3.7
COPY . /application 
RUN pip3 install -r /application/recruitment-challenge-1/requirements.txt
ENV FLASK_APP=/application/recruitment-challenge-1/tiny_app.py
CMD ["flask", "run", "--host", "0.0.0.0"]
