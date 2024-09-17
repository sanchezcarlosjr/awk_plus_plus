FROM python:3.9-slim

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y make g++ build-essential libmagic-dev

RUN pip install awk_plus_plus

ENV GRADIO_SERVER_NAME="0.0.0.0"

EXPOSE 7860

CMD ["cti", "run-webservice"]
