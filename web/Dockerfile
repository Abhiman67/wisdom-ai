FROM node:18-alpine AS base
WORKDIR /app

# Install dependencies first (better caching)
COPY package*.json ./
RUN npm ci --no-audit --no-fund

# Build
COPY . .
# Ensure Next reads env at runtime; we don't bake secrets here
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# Runtime image
FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=base /app/package*.json ./
RUN npm ci --omit=dev --no-audit --no-fund
COPY --from=base /app/.next ./.next
COPY --from=base /app/public ./public
COPY --from=base /app/next.config.js ./next.config.js
COPY --from=base /app/tailwind.config.ts ./tailwind.config.ts
COPY --from=base /app/postcss.config.js ./postcss.config.js
COPY --from=base /app/tsconfig.json ./tsconfig.json

EXPOSE 3000
CMD ["npm", "start"]
