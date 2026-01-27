# Stage 1: Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copia i file di configurazione
COPY package*.json ./

# Installa tutte le dipendenze (incluse devDependencies) per il build
RUN npm ci

# Copia il codice sorgente
COPY . .

# Build dell'applicazione
RUN npm run build

# Stage 2: Production stage con nginx
FROM nginx:alpine

# Copia i file buildati
COPY --from=builder /app/dist /usr/share/nginx/html

# Copia la configurazione nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Espone la porta 80
EXPOSE 81

# Comando di avvio
CMD ["nginx", "-g", "daemon off;"]