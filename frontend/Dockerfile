FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

RUN rm -rf node_modules package-lock.json

RUN npm install
RUN npm install -D vite

COPY . .

EXPOSE 5500

CMD ["npm", "run", "dev"]
