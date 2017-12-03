from datetime import datetime, timedelta
from pandas_datareader import RemoteDataError
import pandas_datareader.data as web
import psycopg2
import logging

from .confparser import ConfParser

COL_ID = 0
COL_TYPE = 1
COL_TICKER_Y = 2

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class AssetsPricer:
    '''Main class of AssetsPricer '''

    def __init__(self, conf_path):
        self.conf = ConfParser(conf_path)

    def insert_price_history(self, instrument_id):
        conn = self.get_db_connection()

        instrument = self.get_instrument(conn, instrument_id)
        prices = self.download_instrument_prices(instrument, max_days=365 * 10)
        self.update_instrument_prices(conn, instrument, prices)

        self.close_db_connection(conn)

    def update_daily_prices(self):
        conn = self.get_db_connection()

        logger.info('Requesting list of instruments from DB.')
        instruments = self.get_instruments(conn)
        logger.info('Downloading prices from Internet.')
        for i in instruments:
            prices = self.download_instrument_prices(i)
            self.update_instrument_prices(conn, i, prices)
        logger.info('Finished downloading prices from Internet.')

        self.close_db_connection(conn)
        logger.info('Closing down.')

    def get_instrument(self, conn, instrument_id):
        cur = conn.cursor()
        cur.execute("""
            SELECT
                i.id,
                i.type_id,
                i.ticker_yahoo
            FROM finance.instruments i
            WHERE i.id = {};""".format(instrument_id))

        row = cur.fetchone()
        instrument = {'id': row[COL_ID], 'type': row[COL_TYPE], 'ticker_y': row[COL_TICKER_Y]}

        cur.close()
        return instrument

    def get_instruments(self, conn):
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT
                i.id,
                i.type_id,
                i.ticker_yahoo
            FROM finance.positions p
            INNER JOIN finance.instruments i
                ON p.instrument_id = i.id
            WHERE i.ticker_yahoo is not null;
            """)

        rows = cur.fetchall()
        instruments = []
        for r in rows:
            instruments.append({'id': r[COL_ID], 'type': r[COL_TYPE],
                                'ticker_y': r[COL_TICKER_Y]})

        cur.close()
        return instruments

    def download_instrument_prices(self, instrument, max_days=2, end_date=datetime.today()):
        prices = {}

        if instrument['type'] == 2:
            start_date = end_date - timedelta(days=max_days + 5)

            try:
                df = web.DataReader(instrument['ticker_y'], 'yahoo', start_date, end_date)
            except RemoteDataError as e:
                logger.error("RemoteDataError: Unable to read URL.")

            for date, daily_prices in df[-max_days:].iterrows():
                prices[date.date()] = {'open': daily_prices[0], 'close': daily_prices[3],
                                       'adj_close': daily_prices[4], 'volume': daily_prices[5]}

        return prices

    def update_instrument_prices(self, conn, instrument, prices):
        if prices:
            cur = conn.cursor()
            for date, daily_prices in prices.items():
                try:
                    cur.execute("""
                        INSERT INTO finance.prices (instrument_id, date, open, close, adj_close, volume)
                        VALUES ({}, '{}', {}, {}, {}, {})
                        ON CONFLICT (instrument_id, date)
                        DO UPDATE SET open = EXCLUDED.open, close = EXCLUDED.close,
                                      adj_close = EXCLUDED.adj_close, volume = EXCLUDED.volume;
                        """.format(instrument['id'], date, daily_prices['open'], daily_prices['close'],
                                   daily_prices['adj_close'], daily_prices['volume']))
                    conn.commit()
                except Exception as e:
                    logger.error(e)
                    conn.rollback()
            cur.close()

    def get_db_connection(self):
        logger.info('Connecting to DB...')
        try:
            conn = psycopg2.connect(dbname=self.conf.db_name, user=self.conf.db_user,
                                    password=self.conf.db_pass, host=self.conf.db_host,
                                    port=self.conf.db_port)
            logger.info('Acquired DB connection.')
            return conn
        except Exception as e:
            logger.error('Failed to connect to DB!')
            raise e

    def close_db_connection(self, conn):
        conn.close()

# if __name__ == '__main__':
#     ap = AssetsPricer('./assets-pricer.ini')
#     ap.update_daily_prices()
#     ap.insert_price_history(6)
