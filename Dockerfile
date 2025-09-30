# Step 1: Start with an official Python base image.
# 'slim' is a lightweight version, which is great for production.
FROM python:3.11-slim

# Step 2: Set a working directory inside the container.
# All subsequent commands will run from here.
WORKDIR /app

# Step 3: Copy the requirements file first.
# This is a Docker best practice that speeds up future builds by using layer caching.
COPY requirements.txt .

# Step 4: Install all Python dependencies from the requirements file.
# --no-cache-dir makes the final image smaller.
RUN pip install --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt

# Step 5: Copy the rest of your application code into the container.
# The first '.' means "everything from the current directory on your machine".
# The second '.' means "put it in the current working directory (/app) inside the container".
COPY . .

# Step 6: Define the command that will run when the container starts.
# For a Container App Job, we simply execute the main Python script.
CMD ["python", "main.py"]