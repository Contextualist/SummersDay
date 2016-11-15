FROM python:2-alpine

RUN pip install --no-cache-dir flask requests

ADD main.py /
ADD templates /templates/

EXPOSE 80
CMD ["python", "/main.py"]
