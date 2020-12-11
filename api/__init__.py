from flask import Flask, Blueprint
from .nbp_data import manage_db_data
from .routes.rates import rates
from .routes.sales import sales
import api.config


def create_app(conf):
    app = Flask(__name__)
    config.limiter.init_app(app)
    app.config.from_object(conf)
    caches = manage_db_data()
    config.sales_cache = caches[0]
    config.sales_cache_usd = caches[1]
    app.register_blueprint(rates)
    app.register_blueprint(sales)
    return app
