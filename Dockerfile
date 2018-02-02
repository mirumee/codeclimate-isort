FROM python:3

LABEL maintainer="Mirumee Software <hello@mirumee.com>"

WORKDIR /usr/src/app

ADD engine.json .
ADD checker.py .

RUN pip install --no-cache-dir isort

RUN useradd -u 9000 -M -d /usr/src/app app
RUN chown -R app:app /usr/src/app

VOLUME /code
WORKDIR /code

CMD [ "python", "/usr/src/app/checker.py" ]
