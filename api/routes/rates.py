from flask import Blueprint
from flask import request, jsonify, make_response
from api.manage_db import get_db, close_db
from api.nbp_data import YEARS, DATE_FORMAT
import datetime
from api.config import limiter
from api.validators import *

rates = Blueprint('rates', __name__)
MAX_LAST_REQUEST = 100


@limiter.limit('60/day;10/hour')
@rates.route('/api/rates/<date>', methods=['GET'])
def get_rate_for_day(date):
    cursor = get_db().cursor()
    if not validate_date(date):
         return jsonify({'message': 'Incorrect date format.'}), 400
    if (int(date.split('-')[0]) not in YEARS):
        return jsonify({'message': 'No data found for given date.'}), 404
    item = cursor.execute('SELECT rate, interpolated FROM rates WHERE date=?;', (date,)).fetchone()
    close_db()
    return jsonify({'date': date,'rate': item[0], 'interpolated': item[1]}), 200

@limiter.limit('100/day;20/hour')
@rates.route('/api/rates/<start_date>/<end_date>', methods=['GET'])
def get_rates_for_period(start_date, end_date):
    if dates_range_exceeded(start_date, end_date):
        return jsonify({'message': 'Maximum date range exceeded. Maximum amount of days - 366.'}), 400
    if not validate_date(start_date) or not validate_date(end_date) or not is_date_order_correct(start_date, end_date):
         return jsonify({'message': 'Incorrect date format.'}), 400
    cursor = get_db().cursor()
    if (int(start_date.split('-')[0]) not in YEARS or int(end_date.split('-')[0]) not in YEARS):
        return jsonify({'message': 'No data found for given period.'}), 404
    dates = get_dates_range(start_date, end_date)
    items = cursor.execute('SELECT * FROM rates WHERE date IN ({seq});'.format(seq=','.join(['?']*len(dates))), dates).fetchall()
    response = []
    for item in items:
        response.append({'date': item[0], 'rate': item[1], 'interpolated': item[2]})
    close_db()
    return jsonify({'rates': response}), 200

@limiter.limit('100/day;10/hour')
@rates.route('/api/rates/last/<last>')
def get_last_rates(last):
    if int(last) < 0 or int(last) > MAX_LAST_REQUEST:
        return jsonify({'message': 'Incorrect days amount. Maximum amount is 100.'}), 400
    cursor = get_db().cursor()
    items = cursor.execute('SELECT * FROM rates ORDER BY date DESC LIMIT ?;', (last,)).fetchall()
    response = []
    for item in items:
        response.append({'date': item[0], 'rate': item[1], 'interpolated': item[2]})
    close_db()
    return jsonify({'rates': response}), 200
