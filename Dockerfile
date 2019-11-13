FROM python:3.7
COPY . /application 
RUN pip3 install -r /application/api/requirements.txt
ENV FLASK_APP=/application/api/tiny_app.py
CMD ["flask", "run", "--host", "0.0.0.0"]
