FROM node:20-slim AS builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .

ARG VITE_API_URL
ARG VITE_SOLANA_NETWORK
ARG VITE_PACK_WALLET_ADDRESS
ARG VITE_SOL_PER_PACK

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_SOLANA_NETWORK=$VITE_SOLANA_NETWORK
ENV VITE_PACK_WALLET_ADDRESS=$VITE_PACK_WALLET_ADDRESS
ENV VITE_SOL_PER_PACK=$VITE_SOL_PER_PACK

RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
