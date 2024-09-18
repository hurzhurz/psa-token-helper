FROM python:3.12-bookworm

WORKDIR /app

RUN  apt-get update && apt-get install -y --no-install-recommends xvfb qt5dxcb-plugin libasound2 libxkbcommon0 libxdamage1 libnss3 libxcomposite1 libxcursor1 libxtst6 && \
     apt-get clean ; \
     rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir PyQT5 PyQtWebEngine requests

COPY psa-token-helper-auto.py .
COPY run.sh .
RUN chmod a+x run.sh

ENV DISPLAY :99

ENTRYPOINT ["/app/run.sh"]
