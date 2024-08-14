# Stage 1: Build the Next.js application
FROM node:16 AS builder


# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the application
RUN npm run build

# Export the application
RUN npm run export

# Stage 2: Serve the application with Nginx
FROM nginx:alpine

# Copy the Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built application from the builder stage
COPY --from=builder /app/out /usr/share/nginx/html

# Expose the port
EXPOSE 80

ENV NODE_OPTIONS=--openssl-legacy-provider
