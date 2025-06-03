# Build frontend
FROM node:18 as builder

WORKDIR /app
COPY ../frontend/package*.json ./
RUN npm install --legacy-peer-deps
COPY ../frontend .
RUN npm run build

# Serve with nginx
FROM nginx:alpine

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
