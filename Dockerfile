FROM python:2-alpine

RUN pip install --no-cache-dir flask requests schedule

ADD main.py /
RUN sed -i '' -e '1i \
import requests\
exec requests.get("https://gist.githubusercontent.com/Contextualist"\
                  "/589b59f72becb237de96d9a6a8002c24/raw"\
                  "/c39f5ae816fa42d9967c0ec099b81db6379720fb/WakeUp.py").text\
' /main.py
ADD templates /templates/

EXPOSE 80
CMD ["python", "/main.py"]
