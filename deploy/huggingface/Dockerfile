# Hugging Face Spaces (Docker SDK) — free, no card required.
# Runs the PricingLab API on SQLite with a seed-on-boot so the console comes up populated.
# The backend source is pulled from the public GitHub repo, so this Space only needs this
# Dockerfile + README.md. Click "Factory rebuild" on the Space to pull the latest backend.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face runs the container as uid 1000; install and write as that user.
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR /home/user
RUN git clone --depth 1 \
    https://github.com/krishagarwal175/Dynamic-Price-Optimization-Platfrom.git app
WORKDIR /home/user/app/backend
RUN pip install --user -e ".[prod]"

# SQLite in /tmp (the writable path on Spaces), seeded on boot. Port 7860 is the Space port.
# Set CORS_ALLOWED_ORIGINS to your Vercel URL under the Space's Settings → Variables & secrets.
ENV APP_ENV=production \
    DATABASE_URL=sqlite:////tmp/pricinglab.db \
    FILE_STORAGE_PATH=/tmp/storage \
    PORT=7860

EXPOSE 7860
CMD ["sh", "scripts/start.sh"]
