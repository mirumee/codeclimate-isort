FROM python:3-slim

LABEL maintainer "Mirumee Software <hello@mirumee.com>"

ADD engine.json /

WORKDIR /usr/src/app

RUN groupadd -g 9000 app
RUN useradd -u 9000 -g app -M -d /usr/src/app app
RUN chown -R app:app /usr/src/app

ADD checker.py .

RUN pip install --no-cache-dir isort

USER app

VOLUME /code
WORKDIR /code

CMD [ "python", "/usr/src/app/checker.py" ]
