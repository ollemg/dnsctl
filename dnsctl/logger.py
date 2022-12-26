from loguru import logger
from .config import settings
from pathlib import Path

path = Path.home().joinpath('.local/share/dnsctl/log')
format_logger = '<green>{time}</green> | <level>{level}</level> | <blue>{name}:{function}:{line}</blue> - <level>{message}</level>'

logger.add(
    sys.stdout,
    level=settings.system.log.upper(),
    colorize=True,
    format=format_logger,
)

logger.add(
    Path.home().joinpath('.local/share/dnsctl/log'),
    rotation='1 GB',
    level=settings.system.log.upper(),
    format=format_logger,
)
