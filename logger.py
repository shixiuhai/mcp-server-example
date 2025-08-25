import logging
import os
from logging.handlers import TimedRotatingFileHandler
from config import yaml_config

def setup_logger():
    """配置并返回日志记录器"""
    log_config = yaml_config['logging']
    
    logger = logging.getLogger(__name__)
    logger.setLevel(log_config['level'].upper())

    # 确保日志目录存在
    os.makedirs(log_config['dir'], exist_ok=True)

    # 创建格式化器
    formatter = logging.Formatter(log_config['format'])

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器 - 按天轮转并自动清理
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_config['dir'], log_config['file']),
        when='midnight',
        interval=1,
        backupCount=log_config['retention_days']
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()