#!/usr/bin/env python3
import zipfile
from pathlib import Path

PROJECT_NAME = "dwafjibk_complete"

# All the files that will be created
files_to_create = {}

# 1. DOCKER-COMPOSE.YML
files_to_create["docker-compose.yml"] = '''version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: dwafjibk_postgres
    environment:
      POSTGRES_DB: dwafjibk
      POSTGRES_USER: dwafjibk_user
      POSTGRES_PASSWORD: 
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - dwafjibk_network

  redis:
    image: redis:7-alpine
    container_name: dwafjibk_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - dwafjibk_network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: dwafjibk_backend
    environment:
      DB_CONNECTION: pgsql
      DB_HOST: postgres
      DB_PORT: 5432
      DB_DATABASE: dwafjibk
      DB_USERNAME: dwafjibk_user
      DB_PASSWORD: 
      REDIS_HOST: redis
      REDIS_PORT: 6379
    volumes:
      - ./backend:/var/www
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    networks:
      - dwafjibk_network
    command: bash -c "composer install && php artisan migrate --force && php artisan serve --host=0.0.0.0 --port=8000"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: dwafjibk_frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    networks:
      - dwafjibk_network

networks:
  dwafjibk_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
'''

# 2. BACKEND DOCKERFILE
files_to_create["backend/Dockerfile"] = '''FROM php:8.3-fpm

RUN apt-get update && apt-get install -y \\
    libpq-dev \\
    libzip-dev \\
    unzip \\
    git \\
    curl

RUN docker-php-ext-install pdo_pgsql zip pcntl

COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

WORKDIR /var/www
COPY . /var/www

RUN composer install --no-interaction --optimize-autoloader

EXPOSE 9000
CMD ["php-fpm"]
'''

# 3. FRONTEND DOCKERFILE
files_to_create["frontend/Dockerfile"] = '''FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
'''

# 4. FRONTEND PACKAGE.JSON
files_to_create["frontend/package.json"] = '''{
  "name": "dwafjibk-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "@reduxjs/toolkit": "^1.9.0",
    "react-redux": "^8.1.0",
    "@tanstack/react-query": "^5.0.0",
    "react-router-dom": "^6.20.0",
    "tailwindcss": "^3.4.0",
    "framer-motion": "^10.16.0"
  },
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  }
}
'''

# 5. BACKEND COMPOSER.JSON
files_to_create["backend/composer.json"] = '''{
  "name": "dwafjibk/backend",
  "type": "project",
  "require": {
    "php": "^8.2",
    "laravel/framework": "^11.0",
    "tymon/jwt-auth": "^2.0"
  }
}
'''

# 6. ENVIRONMENT FILE
files_to_create[".env.example"] = '''APP_NAME=Dwafjibk
APP_ENV=local
APP_DEBUG=true
APP_URL=http://localhost:8000

DB_CONNECTION=pgsql
DB_HOST=postgres
DB_PORT=5432
DB_DATABASE=dwafjibk
DB_USERNAME=dwafjibk_user
DB_PASSWORD=

JWT_SECRET=your_jwt_secret_here
'''

# 7. README
files_to_create["README.md"] = '''
# Dwafjibk Healthcare Platform

## Quick Start (3 Steps)

1. **Extract and enter folder**
   ```bash
   unzip dwafjibk_complete.zip
   cd dwafjibk_complete
   ```

2. **Start the services**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000

For more details, see the documentation in each subfolder.
'''


def create_project_files(root_path: Path, files: dict[str, str]) -> None:
    for relative_path, content in files.items():
        target_path = root_path / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content, encoding="utf-8")


def create_zip_archive(root_path: Path, project_name: str) -> None:
    archive_path = Path(f"{project_name}.zip")
    with zipfile.ZipFile(archive_path, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(root_path.rglob("*")):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(root_path))


def main() -> None:
    base_path = Path.cwd() / PROJECT_NAME
    base_path.mkdir(parents=True, exist_ok=True)

    print(f"Creating project structure in: {base_path}")
    create_project_files(base_path, files_to_create)

    print(f"Creating zip archive: {PROJECT_NAME}.zip")
    create_zip_archive(base_path, PROJECT_NAME)
    print("Done.")


if __name__ == "__main__":
    main()
