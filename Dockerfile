FROM python:2-alpine

RUN pip install --no-cache-dir flask requests schedule

ADD main.py /
ADD templates /templates/

EXPOSE 80
CMD ["python", "/main.py"]
