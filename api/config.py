from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, application_limits=["600/day", "100/hour"])
sales_cache = {}
rates_cache = {}
sales_cache_usd = {}
class BaseConf(object):
    ORIGINS = ["*"]

class DevelopmentConf(BaseConf):
    DEBUG = True
    TESTING = False
    ENV = "development"
    APPNAME = "salesAPI"
