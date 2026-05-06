FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt && \
    pip3 install --no-cache-dir --no-deps openwakeword==0.6.0

# Pre-download the wake word model so first startup is instant
RUN python3 -c "import openwakeword; openwakeword.utils.download_models(['hey_jarvis_v0.1'])"

COPY backend/ ./backend/
COPY frontend/ ./frontend/

COPY run.sh /run.sh
RUN chmod a+x /run.sh

CMD ["/run.sh"]
