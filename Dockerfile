ARG BUILD_FROM
FROM $BUILD_FROM

# Build deps for onnxruntime (required by openwakeword)
RUN apk add --no-cache gcc g++ musl-dev libffi-dev

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Pre-download the wake word model so startup is fast
RUN python3 -c "import openwakeword; openwakeword.utils.download_models(['hey_jarvis_v0.1'])" || true

COPY backend/ ./backend/
COPY frontend/ ./frontend/

COPY run.sh /run.sh
RUN chmod a+x /run.sh

CMD ["/run.sh"]
