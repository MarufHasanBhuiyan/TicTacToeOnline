# Use Python 3.9 (last version fully compatible with Pygame)
FROM python:3.9-slim

# Install SDL2 dependencies (critical for Pygame)
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up dummy display for Pygame
ENV SDL_VIDEODRIVER=dummy

# Copy and install requirements
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy and run the app
COPY . .
CMD ["python", "app.py"]