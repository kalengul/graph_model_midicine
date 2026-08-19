FROM nginx:alpine

COPY nginx/default.conf /etc/nginx/conf.d/default.conf

HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://127.0.0.1/health/nginx || exit 1

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

