# Stage 1: Base image with Node.js and Python
FROM node:18-slim

# Install Python, pip, venv, and comprehensive LaTeX packages
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv \
    texlive-latex-base texlive-latex-extra texlive-fonts-recommended texlive-fonts-extra \
    latexmk && \
    rm -rf /var/lib/apt/lists/*

# Set up the working directory
WORKDIR /app

# Create Python virtual environment and install dependencies
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the requirements.txt and install Python dependencies
COPY tex_tailor/requirements.txt /app/tex_tailor/requirements.txt
RUN pip install --no-cache-dir -r /app/tex_tailor/requirements.txt

# Copy the rest of the application code
COPY . /app

# Install tex_tailor package in development mode
RUN pip install -e /app

# Set the working directory to the frontend
WORKDIR /app/frontend

# Install Node.js dependencies
RUN npm install

# Build the frontend for production
RUN npm run build

# Expose the port
EXPOSE 3001

# Start the server (Python venv is already in PATH via ENV)
CMD ["npm", "run", "server"]

