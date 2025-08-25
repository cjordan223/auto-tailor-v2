# Stage 1: Base image with Node.js and Python
FROM node:18-slim

# Install Python, pip, and LaTeX (using smaller texlive package for faster builds)
RUN apt-get update && \
    apt-get install -y python3 python3-pip texlive-latex-base texlive-latex-extra texlive-fonts-recommended && \
    rm -rf /var/lib/apt/lists/*

# Set up the working directory
WORKDIR /app

# Copy the requirements.txt and install Python dependencies
COPY tex_tailor/requirements.txt /app/tex_tailor/requirements.txt
RUN pip3 install --no-cache-dir -r /app/tex_tailor/requirements.txt

# Copy the rest of the application code
COPY . /app

# Set the working directory to the frontend
WORKDIR /app/frontend

# Install Node.js dependencies
RUN npm install

# Expose the port
EXPOSE 3001

# Start the server
CMD ["npm", "run", "server"]
