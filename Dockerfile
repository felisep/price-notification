FROM python:3.12-alpine

# Install system dependencies for opencv and playwright
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    libffi-dev \
    openssl-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    tk-dev \
    tcl-dev \
    harfbuzz-dev \
    fribidi-dev \
    libimagequant-dev \
    libxcb-dev \
    libpng-dev

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

# Install playwright browsers
RUN playwright install chromium

COPY . .

# Default to price tracker, but allow override
ENV PROJECT_TYPE=price-tracker

ENTRYPOINT ["sh", "-c", "cd projects/$PROJECT_TYPE && python *.py"]