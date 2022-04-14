import os

STANDARD_FORMAT = '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]' \
                  '[%(levelname)s][%(message)s]'

LOGFILE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"logs")  # log文件的目录

LOGFILE_NAME = 'service.log'  # log文件名

# 如果不存在定义的日志目录就创建一个
if not os.path.isdir(LOGFILE_DIR):
    os.mkdir(LOGFILE_DIR)

# log文件的全路径
LOGFILE_PATH = os.path.join(LOGFILE_DIR, LOGFILE_NAME)

# log配置字典
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': STANDARD_FORMAT
        },
        'simple': {
            'format': STANDARD_FORMAT
        },
    },
    'filters': {},
    'handlers': {
        #打印到终端的日志
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',  # 打印到屏幕
            'formatter': 'standard'
        },
        #打印到文件的日志,收集info及以上的日志
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件
            'formatter': 'standard',
            'filename': LOGFILE_PATH,  # 日志文件
            'maxBytes': 1024*1024*5,  # 日志大小 5M
            'backupCount': 5,
            'encoding': 'utf-8',  # 日志文件的编码
        },
    },
    'loggers': {
        #logging.getLogger(__name__)拿到的logger配置
        '': {
            'handlers': ['default', 'console'],  # 这里把上面定义的两个handler都加上，即log数据既写入文件又打印到屏幕
            'level': 'INFO',
            'propagate': True,  # 向上（更高level的logger）传递
        },
    },
}