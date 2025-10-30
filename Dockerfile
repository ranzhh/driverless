FROM python:3.11-slim

# Install system dependencies for C++ pipeline and Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopencv-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Comment out macOS-specific settings in CMakeLists.txt
RUN sed -i 's|set(CMAKE_OSX_ARCHITECTURES "arm64")|# set(CMAKE_OSX_ARCHITECTURES "arm64")|' CMakeLists.txt && \
    sed -i 's|set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libc++")|# set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libc++")|' CMakeLists.txt && \
    sed -i 's|set(OpenCV_DIR /opt/homebrew/Cellar/opencv/4.12.0_11/lib/cmake/opencv4)|# set(OpenCV_DIR /opt/homebrew/Cellar/opencv/4.12.0_11/lib/cmake/opencv4)|' CMakeLists.txt

# Build the C++ pipeline
RUN make build

# Create necessary directories
RUN mkdir -p output config

# Expose ports for both services
# 7860 for Gradio frontend
# 8080 for legacy compatibility
EXPOSE 7860 8080

# Default command (can be overridden by docker-compose)
CMD ["python", "gradio_app.py"]
