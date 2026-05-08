FROM php:8.3-fpm

RUN apt-get update && apt-get install -y \
    libpq-dev \
    libzip-dev \
    unzip \
    git \
    curl

RUN docker-php-ext-install pdo_pgsql zip pcntl

COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

WORKDIR /var/www
COPY . /var/www

RUN composer install --no-interaction --optimize-autoloader

EXPOSE 9000
CMD ["php-fpm"]
