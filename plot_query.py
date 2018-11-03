import argparse
import os

import pandas as pd
from plotnine import *
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import matplotlib.pylab as plt

_SESSION = None


def get_session():
    global _SESSION

    if _SESSION:
        return _SESSION()

    engine = create_engine(
        os.environ['PLOT_SQL_DB_URL'],
        pool_recycle=60 * 60,
        pool_pre_ping=True,
        implicit_returning=True
    )
    session_factory = sessionmaker(bind=engine)
    _SESSION = scoped_session(session_factory)
    return _SESSION()


def plot_query(query, plot_type):


    session = get_session()

    df = pd.read_sql_query(query, session.bind)
    if plot_type == 'scatter':
        plot = (ggplot(df, aes(df.columns[0], df.columns[1])) + geom_point() + theme_xkcd() + theme(axis_text_x=element_text(rotation=90, hjust=1)))
    elif plot_type == 'hist':
        plot = (
            ggplot(df)
            + geom_col(aes(df.columns[0], df.columns[1]))
            + theme_xkcd() + theme(axis_text_x=element_text(rotation=90, hjust=1))
        )

    plt.show(plot.draw())
    # psql postgres://prix:prix@localhost:5432/prix --field-separator=, -qAt -f


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--sql_file', type=str, required=True,
    )
    parser.add_argument(
        '--plot_type', type=str, default='scatter', choices=['hist', 'scatter']
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    with open(args.sql_file, 'r') as f:
        plot_query(f.read(), args.plot_type)
