
# ===== Stage 1: Build main frontend =====
FROM node:18 as main_front_builder

WORKDIR /app/frontend
COPY ../frontend/package*.json ./
RUN npm install --legacy-peer-deps
COPY ../frontend .
RUN npm run build

FROM node:18 AS mini_front_builder

WORKDIR /app/backend/mini_front
COPY ../backend/mini_front/package*.json ./
RUN npm install --legacy-peer-deps
COPY ../backend/mini_front .
RUN npm run build

# Serve with nginx
FROM nginx:alpine

COPY nginx/default.conf /etc/nginx/conf.d/default.conf

COPY --from=main_front_builder /app/frontend/dist /usr/share/nginx/html
COPY --from=mini_front_builder /app/backend/mini_front/dist /usr/share/nginx/html/mini-front-manager

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
