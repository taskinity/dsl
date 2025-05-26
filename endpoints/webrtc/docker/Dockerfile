FROM node:16-slim

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy server code
COPY server.js .
COPY public/ ./public/

# Expose ports
EXPOSE 3000

# Start server
CMD ["node", "server.js"]
