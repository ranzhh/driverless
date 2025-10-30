FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libopencv-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Comment out macOS-specific settings in CMakeLists.txt
RUN sed -i 's|set(CMAKE_OSX_ARCHITECTURES "arm64")|# set(CMAKE_OSX_ARCHITECTURES "arm64")|' CMakeLists.txt && \
    sed -i 's|set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libc++")|# set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libc++")|' CMakeLists.txt && \
    sed -i 's|set(OpenCV_DIR /opt/homebrew/Cellar/opencv/4.12.0_11/lib/cmake/opencv4)|# set(OpenCV_DIR /opt/homebrew/Cellar/opencv/4.12.0_11/lib/cmake/opencv4)|' CMakeLists.txt

# Build the C++ pipeline
RUN make build

# Create output directory
RUN mkdir -p output

# Copy and make entrypoint script executable
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

EXPOSE 8080

# Use entrypoint script
CMD ["./docker-entrypoint.sh"]
