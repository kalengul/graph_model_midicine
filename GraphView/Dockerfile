#Сборка React App
#Задаем образ node:18 в качестве базового образа и присваиваем имя build-stage
FROM node:18 AS build-stage
#Создаем рабочую директорию
WORKDIR /app/client
#Копируем в рабочую папку файлы package
COPY view/package.json view/package-lock.json ./
#Устанавливаем необходимые зависимости
RUN npm install --only=prod --legacy-peer-deps
#Копируем остальное содержимое в рабочую директорию и собираем React приложение
COPY view/ ./
RUN npm run build

#Сборка Node Server
FROM node:18
WORKDIR /app
COPY Server/package.json Server/package-lock.json ./
RUN npm install
COPY Server/ ./

#Копируем собранное React-приложение в директорию ./public текущего образа.
COPY --from=build-stage /app/client/build ./public

#Указываем, что контейнер будет прослушивать порт 3000
EXPOSE 3000
#Команда по умолчанию, которая будет выполнена при запуске контейнера.
CMD ["node", "index.js"]