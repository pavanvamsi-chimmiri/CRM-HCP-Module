# Frontend service for AI CRM

FROM node:20-alpine AS base

WORKDIR /app

# -----------------------------------------------------------------------------
# Dependencies stage
# -----------------------------------------------------------------------------
FROM base AS dependencies

COPY package.json package-lock.json* ./
RUN npm ci

# -----------------------------------------------------------------------------
# Development stage
# -----------------------------------------------------------------------------
FROM dependencies AS development

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# -----------------------------------------------------------------------------
# Build stage
# -----------------------------------------------------------------------------
FROM dependencies AS build

COPY . .

ARG VITE_API_BASE_URL=http://localhost:8000/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# -----------------------------------------------------------------------------
# Production stage (nginx)
# -----------------------------------------------------------------------------
FROM nginx:alpine AS production

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost:80 || exit 1

CMD ["nginx", "-g", "daemon off;"]
