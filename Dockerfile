FROM node:24-alpine

WORKDIR /app

# Copy package descriptors first to optimize Docker layer caching
COPY package*.json ./

RUN npm install

# Copy TypeScript configuration and source files
COPY tsconfig.json ./
COPY src/ ./src/

# Create data directory for state persistence
RUN mkdir -p /app/data

EXPOSE 5000

ENV PORT=5000
ENV NODE_ENV=production

CMD ["npm", "start"]
