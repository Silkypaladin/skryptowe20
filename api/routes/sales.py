from flask import Blueprint
from flask import request, jsonify, make_response
from api.manage_db import get_db, close_db
from api.nbp_data import YEARS, DATE_FORMAT, Currencies, DB_DATE_FORMAT
import datetime
import api.config
from api.validators import *
from api.config import limiter

sales = Blueprint('sales', __name__)

@limiter.limit('60/day;10/hour')
@sales.route('/api/sales/<date>', methods=['GET'])
def get_sales_for_day( date):
    cursor = get_db().cursor()
    if not validate_date(date):
         return jsonify({'message': 'Incorrect date format.'}), 400
    if (int(date.split('-')[0]) not in YEARS):
        return jsonify({'message': 'No data found for given date.'}), 404
    if date in api.config.sales_cache and date in api.config.sales_cache_usd:
        sale_pln = api.config.sales_cache[date]
        sale_usd = api.config.sales_cache_usd[date]
        return jsonify({'date': date, 'pln': {'sale': sale_pln[0]}, 'usd' : {'sale': sale_usd[0]}}), 200
    else:
        cursor = get_db().cursor()
        sale = cursor.execute('SELECT SUM(sales) FROM sales WHERE orderdate=? GROUP BY orderdate;', (datetime.datetime.strptime(date, DATE_FORMAT).strftime(DB_DATE_FORMAT),)).fetchall()
        if sale == []:
            close_db()
            return jsonify({'message': 'No data found for given date.'}), 404
        rate = cursor.execute('SELECT rate, interpolated FROM rates WHERE date=?;', (date,)).fetchall()
        return jsonify({'date': date, 'pln': {'sale': round(sale[0] * rate[0], 4)}, 'usd' : {'sale': round(sale[0], 4)}})

@limiter.limit('100/day;20/hour')
@sales.route('/api/sales/<start_date>/<end_date>', methods=['GET'])
def get_sales_for_days_range(start_date, end_date):
    if dates_range_exceeded(start_date, end_date):
        return jsonify({'message': 'Maximum date range exceeded. Maximum amount of days - 366.'}), 400
    if not validate_date(start_date) or not validate_date(end_date) or not is_date_order_correct(start_date, end_date):
        return jsonify({'message': 'Incorrect date format.'}), 400
    if (int(start_date.split('-')[0]) not in YEARS) or (int(end_date.split('-')[0]) not in YEARS):
        return jsonify({'message': 'No data found for given period.'}), 404
    dates = get_dates_range(start_date, end_date)
    response = []
    for date in dates:
        if date in api.config.sales_cache and date in api.config.sales_cache_usd:
            response.append({'date': date, 'pln': {'sale': api.config.sales_cache[date][0]}, 'usd' : {'sale': api.config.sales_cache_usd[date][0]}})
        else:
            response.append({'date': date, 'pln': {'sale': 0}, 'usd' : {'sale': 0}})
    return jsonify({'sales': response}), 200
