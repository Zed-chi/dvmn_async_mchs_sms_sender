# dvmn_async_mchs_sms_sender

## Проект "Рассылаем СМС для МЧС"

Веб-приложение на основе Quart сервера, которое помогает рассылать и контролировать процесс рассылки смс.

### Для запуска требуется:
* Установленный Redis
* python 3.7 и выше
* установка зависимосте командой :
    `pip install -r requirements.txt`
* запуск командой:
    `python trio_server.py`

Для запуска требуются аргументы:
--address - адрес Redis сервера (по-умолчанию "redis://localhost:6379")
--password - пароль от Redis сервера (по-умолчанию "")


## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).