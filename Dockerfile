# Use the official lightweight Python image
# We explicitly use 3.11 for prebuilt wheel compatibility
FROM python:3.11-slim

# Install system dependencies
# cmake and build-essential are strictly required to build dlib from C++ source
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY backend/requirements.txt .

# Optimize the build to prevent Out-Of-Memory errors on free hosting
# This restricts the C++ compiler to 1 thread instead of maxing the CPU
ENV CMAKE_BUILD_PARALLEL_LEVEL=1

# Upgrade pip and install the Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir cmake
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend source code
COPY backend/ /app/

# Expose the port Render expects to route internet traffic through
EXPOSE 10000

# Start the FastAPI application via Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
