#! /usr/bin/env python
# coding:utf-8

from __future__ import division, print_function
import collections
import sqlite3
# import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, TEXT, INTEGER, REAL
from sqlalchemy.orm import sessionmaker
# smt
from smt.db.createdb import Sentence
from smt.langmodel.ngram import ngram
import math


def _create_ngram_count_db(lang, langmethod=lambda x: x,
                           n=3, db="sqilte:///:memory:"):
    engine = create_engine(db)
    # create session
    Session = sessionmaker(bind=engine)
    session = Session()

    query = session.query(Sentence)

    ngram_dic = collections.defaultdict(float)
    for item in query:
        if lang == 1:
            sentences = langmethod(item.lang1).split()
        elif lang == 2:
            sentences = langmethod(item.lang2).split()
        sentences = ["</s>", "<s>"] + sentences + ["</s>"]
        ngrams = ngram(sentences, n)
        for tpl in ngrams:
            ngram_dic[tpl] += 1

    return ngram_dic


def create_ngram_count_db(lang, langmethod=lambda x: x,
                          n=3, db="sqilte:///:memory:"):
    engine = create_engine(db)
    # create session
    Session = sessionmaker(bind=engine)
    session = Session()

    class Trigram(declarative_base()):
        __tablename__ = 'lang{}trigram'.format(lang)
        id = Column(INTEGER, primary_key=True)
        first = Column(TEXT)
        second = Column(TEXT)
        third = Column(TEXT)
        count = Column(INTEGER)

    # create table
    Trigram.__table__.drop(engine, checkfirst=True)
    Trigram.__table__.create(engine)

    ngram_dic = _create_ngram_count_db(lang, langmethod=langmethod, n=n, db=db)

    # insert items
    for (first, second, third), count in ngram_dic.items():
        print(u"inserting {}, {}, {}".format(first, second, third))
        item = Trigram(first=first,
                       second=second,
                       third=third,
                       count=count)
        session.add(item)
    session.commit()


# create views using SQLite3
def create_ngram_count_without_last_view(lang, db=":memory:"):
    # create phrase_count table
    fromtablename = "lang{}trigram".format(lang)
    table_name = "lang{}trigram_without_last".format(lang)
    # create connection
    con = sqlite3.connect(db)
    cur = con.cursor()
    try:
        cur.execute("drop view {0}".format(table_name))
    except sqlite3.Error:
        print("{0} view does not exists.\n\
              => creating a new view".format(table_name))
    cur.execute("""create view {}
                as select first, second, sum(count) as count from
                {} group by first, second order by count
                desc""".format(table_name, fromtablename))
    con.commit()


def create_ngram_prob(lang,
                      db=":memory:"):

    # Create connection in sqlite3 to use view
    table_name = "lang{}trigram_without_last".format(lang)
    # create connection
    con = sqlite3.connect(db)
    cur = con.cursor()

    class Trigram(declarative_base()):
        __tablename__ = 'lang{}trigram'.format(lang)
        id = Column(INTEGER, primary_key=True)
        first = Column(TEXT)
        second = Column(TEXT)
        third = Column(TEXT)
        count = Column(INTEGER)

    class TrigramProb(declarative_base()):
        __tablename__ = 'lang{}trigramprob'.format(lang)
        id = Column(INTEGER, primary_key=True)
        first = Column(TEXT)
        second = Column(TEXT)
        third = Column(TEXT)
        prob = Column(REAL)

    class TrigramProbWithoutLast(declarative_base()):
        __tablename__ = 'lang{}trigramprob_without_last'.format(lang)
        id = Column(INTEGER, primary_key=True)
        first = Column(TEXT)
        second = Column(TEXT)
        prob = Column(REAL)

    # create connection in SQLAlchemy
    sqlalchemydb = "sqlite:///{}".format(db)
    engine = create_engine(sqlalchemydb)
    # create session
    Session = sessionmaker(bind=engine)
    session = Session()
    # create table
    TrigramProb.__table__.drop(engine, checkfirst=True)
    TrigramProb.__table__.create(engine)
    TrigramProbWithoutLast.__table__.drop(engine, checkfirst=True)
    TrigramProbWithoutLast.__table__.create(engine)

    # calculate total number
    query = session.query(Trigram)
    totalnumber = len(query.all())

    # get trigrams
    query = session.query(Trigram)
    for item in query:
        first, second, third = item.first, item.second, item.third
        count = item.count

        cur.execute("""select * from {} where \
                    first=? and\
                    second=?""".format(table_name),
                    (first, second))
        one = cur.fetchone()
        # if fetch is failed, one is NONE (no exceptions are raised)
        if not one:
            print("not found correspont first and second")
            continue
        else:
            alpha = 0.00017
            c = count
            n = one[2]
            v = totalnumber
            # create logprob
            logprob = math.log((c + alpha) / (n + alpha * v))
            print(u"{}, {}, {}:\
                  log({} + {} / {} + {} + {}) = {}".format(first,
                                                           second,
                                                           third,
                                                           c,
                                                           alpha,
                                                           n,
                                                           alpha,
                                                           v,
                                                           logprob))
            trigramprob = TrigramProb(first=first,
                                      second=second,
                                      third=third,
                                      prob=logprob)
            session.add(trigramprob)
            # for without last
            logprobwithoutlast = math.log(alpha / (n + alpha * v))
            print(u"{}, {}, {}:\
                  log({} / {} + {} + {}) = {}".format(first,
                                                      second,
                                                      third,
                                                      alpha,
                                                      n,
                                                      alpha,
                                                      v,
                                                      logprobwithoutlast))
            probwl = TrigramProbWithoutLast(first=first,
                                            second=second,
                                            prob=logprobwithoutlast)
            session.add(probwl)
    session.commit()


def create_ngram_db(lang, langmethod=lambda x: x,
                    n=3, db=":memory:"):

    sqlalchemydb = "sqlite:///{}".format(db)
    create_ngram_count_db(lang=lang, langmethod=langmethod,
                          n=n,
                          db=sqlalchemydb)
    create_ngram_count_without_last_view(lang=lang, db=db)
    create_ngram_prob(lang=lang, db=db)


if __name__ == '__main__':
    pass
