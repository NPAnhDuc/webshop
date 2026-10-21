FROM node:20-alpine

WORKDIR /app

# Copy package descriptors first to optimize Docker layer caching
COPY package*.json ./

RUN npm install

# Copy TypeScript configuration, source files, initial state, and images
COPY tsconfig.json ./
COPY src/ ./src/
COPY data/ ./data/
COPY public/ ./public/

EXPOSE 5000

ENV PORT=5000
ENV NODE_ENV=production

CMD ["npm", "start"]
