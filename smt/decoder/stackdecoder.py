#! /usr/bin/env python
# coding:utf-8

from __future__ import division, print_function
import math
# sqlalchemy
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, TEXT, REAL, INTEGER
from sqlalchemy.orm import sessionmaker


# prepare classes for sqlalchemy
class Phrase(declarative_base()):
    __tablename__ = "phrase"
    id = Column(INTEGER, primary_key=True)
    lang1p = Column(TEXT)
    lang2p = Column(TEXT)


class TransPhraseProb(declarative_base()):
    __tablename__ = "phraseprob"
    id = Column(INTEGER, primary_key=True)
    lang1p = Column(TEXT)
    lang2p = Column(TEXT)
    p1_2 = Column(REAL)
    p2_1 = Column(REAL)


def phrase_prob(lang1p, lang2p,
                transfrom=2,
                transto=1,
                db="sqlite:///:memory:",
                init_val=1.0e-10):
    """
    """
    engine = create_engine(db)
    Session = sessionmaker(bind=engine)
    session = Session()
    # search
    query = session.query(TransPhraseProb).filter_by(lang1p=lang1p,
                                                     lang2p=lang2p)
    if transfrom == 2 and transto == 1:
        try:
            # Be Careful! The order of conditional prob is reversed
            # as transfrom and transto because of bayes rule
            return query.one().p2_1
        except sqlalchemy.orm.exc.NoResultFound:
            return init_val
    elif transfrom == 1 and transto == 2:
        try:
            return query.one().p1_2
        except sqlalchemy.orm.exc.NoResultFound:
            return init_val


def available_phrases(inputs, transfrom=2, transto=1, db="sqlite:///:memory:"):
    """
    >>> decode.available_phrases(u"He is a teacher.".split(),
                                 db_name="sqlite:///:db:"))
    set([((1, u'He'),),
         ((1, u'He'), (2, u'is')),
         ((2, u'is'),),
         ((2, u'is'), (3, u'a')),
         ((3, u'a'),),
         ((4, u'teacher.'),)])
    """
    engine = create_engine(db)
    # create session
    Session = sessionmaker(bind=engine)
    session = Session()
    available = set()
    for i, f in enumerate(inputs):
        f_rest = ()
        for fr in inputs[i:]:
            f_rest += (fr,)
            rest_phrase = u" ".join(f_rest)
            if transfrom == 2 and transto == 1:
                query = session.query(Phrase).filter_by(lang2p=rest_phrase)
            elif transfrom == 1 and transto == 2:
                query = session.query(Phrase).filter_by(lang1p=rest_phrase)
            lst = list(query)
            if lst:
                available.add(tuple(enumerate(f_rest, i+1)))
    return available


class HypothesisBase(object):
    def __init__(self,
                 db,
                 sentences,
                 ngram,
                 ngram_words,
                 inputps_with_index,
                 outputps,
                 transfrom,
                 transto,
                 covered,
                 remained,
                 start,
                 end,
                 prev_start,
                 prev_end,
                 remain_phrases,
                 prob,
                 prev_hypo
                 ):

        self._db = db
        self._sentences = sentences
        self._ngram = ngram
        self._ngram_words = ngram_words
        self._inputps_with_index = inputps_with_index
        self._outputps = outputps
        self._transfrom = transfrom
        self._transto = transto
        self._covered = covered
        self._remained = remained
        self._start = start
        self._end = end
        self._prev_start = prev_start
        self._prev_end = prev_end
        self._remain_phrases = remain_phrases
        self._prob = prob
        self._prev_hypo = prev_hypo

        self._output_sentences = outputps

    @property
    def db(self):
        return self._db

    @property
    def sentences(self):
        return self._sentences

    @property
    def ngram(self):
        return self._ngram

    @property
    def ngram_words(self):
        return self._ngram_words

    @property
    def inputps_with_index(self):
        return self._inputps_with_index

    @property
    def outputps(self):
        return self._outputps

    @property
    def transfrom(self):
        return self._transfrom

    @property
    def transto(self):
        return self._transto

    @property
    def covered(self):
        return self._covered

    @property
    def remained(self):
        return self._remained

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    @property
    def prev_start(self):
        return self._prev_start

    @property
    def prev_end(self):
        return self._prev_end

    @property
    def remain_phrases(self):
        return self._remain_phrases

    @property
    def prob(self):
        return self._prob

    @property
    def prev_hypo(self):
        return self._prev_hypo

    @property
    def output_sentences(self):
        return self._output_sentences

    def __unicode__(self):
        d = [("db", self._db),
             ("sentences", self._sentences),
             ("inputps_with_index", self._inputps_with_index),
             ("outputps", self._outputps),
             ("ngram", self._ngram),
             ("ngram_words", self._ngram_words),
             ("transfrom", self._transfrom),
             ("transto", self._transto),
             ("covered", self._covered),
             ("remained", self._remained),
             ("start", self._start),
             ("end", self._end),
             ("prev_start", self._prev_start),
             ("prev_end", self._prev_end),
             ("remain_phrases", self._remain_phrases),
             ("prob", self._prob)
             #("prev_hypo", ""),
             ]
        return u"Hypothesis Object\n" +\
               u"\n".join([u" " + k + u": " +
                           unicode(v) for (k, v) in d])

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __hash__(self):
        return hash(unicode(self))


class Hypothesis(HypothesisBase):
    """
    Realize like the following class

    >>> args = {"sentences": sentences,
    ... "inputps_with_index": phrase,
    ... "outputps": outputps,
    ... "covered": hyp0.covered.union(set(phrase)),
    ... "remained": hyp0.remained.difference(set(phrase)),
    ... "start": phrase[0][0],
    ... "end": phrase[-1][0],
    ... "prev_start": hyp0.start,
    ... "prev_end": hyp0.end,
    ... "remain_phrases": remain_phrases(phrase,
    ... hyp0.remain_phrases),
    ... "prev_hypo": hyp0
    ... }

    >>> hyp1 = decode.HypothesisBase(**args)
    """

    def __init__(self,
                 prev_hypo,
                 inputps_with_index,
                 outputps,
                 ):

        start = inputps_with_index[0][0]
        end = inputps_with_index[-1][0]
        prev_start = prev_hypo.start
        prev_end = prev_hypo.end
        args = {"db": prev_hypo.db,
                "prev_hypo": prev_hypo,
                "sentences": prev_hypo.sentences,
                "ngram": prev_hypo.ngram,
                # set later
                "ngram_words": prev_hypo.ngram_words,
                "inputps_with_index": inputps_with_index,
                "outputps": outputps,
                "transfrom": prev_hypo.transfrom,
                "transto": prev_hypo.transto,
                "covered": prev_hypo.covered.union(set(inputps_with_index)),
                "remained": prev_hypo.remained.difference(
                    set(inputps_with_index)),
                "start": start,
                "end": end,
                "prev_start": prev_start,
                "prev_end": prev_end,
                "remain_phrases": self._calc_remain_phrases(
                    inputps_with_index,
                    prev_hypo.remain_phrases),
                # set later
                "prob": 1
                }
        HypothesisBase.__init__(self, **args)
        # set ngram words
        self._ngram_words = self._set_ngram_words()
        # set the exact probability
        self._prob = self._cal_prob(start - prev_end)
        # set the output phrases
        self._output_sentences = prev_hypo.output_sentences + outputps

    def _set_ngram_words(self):
        lst = self._prev_hypo.ngram_words + list(self._outputps)
        return list(reversed(list(reversed(lst))[:self._ngram]))

    def _cal_phrase_prob(self):
        inputp = u" ".join(zip(*self._inputps_with_index)[1])
        outputp = u" ".join(self._outputps)

        if self._transfrom == 2 and self._transto == 1:
            return phrase_prob(lang1p=outputp,
                               lang2p=inputp,
                               transfrom=self._transfrom,
                               transto=self._transto,
                               db=self._db,
                               init_val=1.0e-10)
        elif self._transfrom == 1 and self._transto == 2:
            return phrase_prob(lang1p=inputp,
                               lang2p=outputp,
                               transfrom=self._transfrom,
                               transto=self._transto,
                               db=self._db,
                               init_val=1.0e-10)
        else:
            raise Exception("specify transfrom and transto")

    def _cal_prob(self, dist):
        val = self._prev_hypo.prob *\
            self._reordering_model(0.1, dist) *\
            self._cal_phrase_prob()
        return val

    def _reordering_model(self, alpha, dist):
        return math.pow(alpha, math.fabs(dist))

    def _calc_remain_phrases(self, phrase, phrases):
        """
        >>> res = remain_phrases(((2, u'is'),),
        set([((1, u'he'),),
        ((2, u'is'),),
        ((3, u'a'),),
        ((2, u'is'),
        (3, u'a')),
        ((4, u'teacher'),)]))
        set([((1, u'he'),), ((3, u'a'),), ((4, u'teacher'),)])
        >>> res = remain_phrases(((2, u'is'), (3, u'a')),
        set([((1, u'he'),),
        ((2, u'is'),),
        ((3, u'a'),),
        ((2, u'is'),
        (3, u'a')),
        ((4, u'teacher'),)]))
        set([((1, u'he'),), ((4, u'teacher'),)])
        """
        s = set()
        for ph in phrases:
            for p in phrase:
                if p in ph:
                    break
            else:
                s.add(ph)
        return s


def create_empty_hypothesis(sentences, ngram=3, transfrom=2, transto=1,
                            db="sqlite:///:memory:"):
    phrases = available_phrases(sentences,
                                db=db)
    hyp0 = HypothesisBase(sentences=sentences,
                          db=db,
                          inputps_with_index=(),
                          outputps=[],
                          ngram=ngram,
                          ngram_words=["<S>"]*ngram,
                          transfrom=transfrom,
                          transto=transto,
                          covered=set(),
                          start=0,
                          end=0,
                          prev_start=0,
                          prev_end=0,
                          remained=set(enumerate(sentences, 1)),
                          remain_phrases=phrases,
                          prev_hypo=None,
                          prob=1)
    return hyp0


class Stack(set):
    def __init__(self, size=10,
                 histogram_pruning=True,
                 threshold_pruning=False):
        set.__init__(self)
        self._min_hyp = None
        self._max_hyp = None
        self._size = size
        self._histogram_pruning = histogram_pruning
        self._threshold_pruning = threshold_pruning

    def add_hyp(self, hyp):
        prob = hyp.prob
        # for the first time
        if self == set([]):
            self._min_hyp = hyp
            self._max_hyp = hyp
        else:
            if self._min_hyp.prob > prob:
                self._min_hyp = hyp
            if self._max_hyp.prob < prob:
                self._max_hyp = hyp
        self.add(hyp)

    def _get_min_hyp(self):
        # set value which is more than 1
        lst = list(self)
        mn = lst[0]
        for item in self:
            if item.prob < mn.prob:
                mn = item
        return mn

    def add_with_combine_prune(self, hyp):
        prob = hyp.prob
        if self == set([]):
            self._min_hyp = hyp
            self._max_hyp = hyp
        else:
            if self._min_hyp.prob > prob:
                self._min_hyp = hyp
            if self._max_hyp.prob < prob:
                self._max_hyp = hyp
        self.add(hyp)
        # combine
        for _hyp in self:
            if hyp.ngram_words[:-1] == _hyp.ngram_words[:-1] and \
                    hyp.end == hyp.end:
                if hyp.prob > _hyp:
                    self.remove(_hyp)
                    self.add(hyp)
                    break
        # histogram pruning
        if self._histogram_pruning:
            if len(self) > self._size:
                self.remove(self._min_hyp)
                self._min_hyp = self._get_min_hyp()
        # threshold pruning
        if self._threshold_pruning:
            alpha = 1.0e-5
            if hyp.prob < self._max_hyp * alpha:
                self.remove(hyp)


def stack_decoder(sentence, transfrom=2, transto=1,
                  stacksize=10,
                  lang1method=lambda x: x,
                  lang2method=lambda x: x,
                  db="sqlite:///:memory:"):
    # create phrase_prob table
    engine = create_engine(db)
    # create session
    Session = sessionmaker(bind=engine)
    session = Session()

    if transfrom == 2 and transto == 1:
        sentences = lang2method(sentence)
    else:
        sentences = lang1method(sentence)
    # create stacks
    len_sentences = len(sentences)
    stacks = [Stack(size=stacksize,
                    histogram_pruning=True,
                    threshold_pruning=False,
                    ) for i in range(len_sentences+1)]
    # create the initial hypothesis
    hyp0 = create_empty_hypothesis(sentences=sentences,
                                   ngram=3,
                                   transfrom=2,
                                   transto=1,
                                   db=db)
    stacks[0].add_hyp(hyp0)

    # main loop
    for i, stack in enumerate(stacks):
        for hyp in stack:
            for phrase in hyp.remain_phrases:
                phrase_str = u" ".join(zip(*phrase)[1])
                if transfrom == 2 and transto == 1:
                    query = session.query(TransPhraseProb).filter_by(
                        lang2p=phrase_str).order_by(
                            sqlalchemy.desc(TransPhraseProb.p2_1))[:10]
                elif transfrom == 1 and transto == 2:
                    query = session.query(TransPhraseProb).filter_by(
                        lang1p=phrase_str).order_by(
                            sqlalchemy.desc(TransPhraseProb.p1_2))[:10]
                query = list(query)
                for item in query:
                    if transfrom == 2 and transto == 1:
                        outputp = item.lang1p
                    elif transfrom == 1 and transto == 2:
                        outputp = item.lang2p
                    #print(u"calculating\n {0} = {1}\n in stack {2}".format(
                    #      phrase, outputp, i))
                    if transfrom == 2 and transto == 1:
                        outputps = lang1method(outputp).split()
                    elif transfrom == 1 and transto == 2:
                        outputps = lang2method(outputp).split()
                    # place in stack
                    # and recombine with existing hypothesis if possible
                    new_hyp = Hypothesis(prev_hypo=hyp,
                                         inputps_with_index=phrase,
                                         outputps=outputps)
                    print("loop: ", i, "len:", len(new_hyp.covered))
                    stacks[len(new_hyp.covered)].add_with_combine_prune(
                        new_hyp)
    return stacks


if __name__ == '__main__':
    pass
