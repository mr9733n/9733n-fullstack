import logging
import os
from logging.handlers import TimedRotatingFileHandler

LOG_DIR = "api/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Создаем TimedRotatingFileHandler для ротации логов по дате
log_file_handler = TimedRotatingFileHandler(
    filename=os.path.join(LOG_DIR, "app_log.txt"),  # Основной файл лога
    when="midnight",  # Ротация логов каждый день в полночь
    interval=1,       # Интервал ротации (1 день)
    backupCount=7,    # Хранить 7 архивных логов
    encoding="utf-8"  # Кодировка файла логов
)

log_file_handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))

# Конфигурация логгера
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        log_file_handler,          # Логи в файл с ротацией
        logging.StreamHandler()    # Логи в консоль
    ]
)

logger = logging.getLogger("9733n API")
