#! /usr/bin/env python
# coding:utf-8

import unittest
from fractions import Fraction as Frac
from smt.decoder.stackdecoder import _future_cost_estimate
from smt.decoder.stackdecoder import _create_estimate_dict
from smt.decoder.stackdecoder import ArgumentNotSatisfied
from smt.decoder.stackdecoder import future_cost_estimate
from smt.decoder.stackdecoder import TransPhraseProb
# sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class FutureCostEstimateTest(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_future_cost_estimate(test):
        sentences = u"the tourism initiative addresses this\
            for the first time".split()
        transfrom = 2
        transto = 1
        init_val = 100.0
        db = "sqlite:///:memory:"

        engine = create_engine(db)
        Session = sessionmaker(bind=engine)
        session = Session()
        future_cost_estimate(sentences,
                             transfrom=transfrom,
                             transto=transto,
                             init_val=init_val,
                             db=db)

    def test_text_example(self):
        sentences = u"the tourism initiative addresses this\
            for the first time".split()
        phrase_prob = {(1, 1): Frac(-1),
                       (2, 2): Frac(-2),
                       (3, 3): Frac(-15, 10),
                       (4, 4): Frac(-24, 10),
                       (5, 5): Frac(-14, 10),
                       (6, 6): Frac(-1),
                       (7, 7): Frac(-1),
                       (8, 8): Frac(-19, 10),
                       (9, 9): Frac(-16, 10),
                       (3, 4): Frac(-4),
                       (5, 6): Frac(-25, 10),
                       (7, 8): Frac(-22, 10),
                       (6, 7): Frac(-13, 10),
                       (8, 9): Frac(-24, 10),
                       (5, 7): Frac(-27, 10),
                       (6, 8): Frac(-23, 10),
                       (7, 9): Frac(-23, 10),
                       (6, 9): Frac(-23, 10),
                       }
        ans = _future_cost_estimate(sentences,
                                    phrase_prob)
        val = {(1, 1): Frac(-1),
               (1, 2): Frac(-3),
               (1, 3): Frac(-45, 10),
               (1, 4): Frac(-69, 10),
               (1, 5): Frac(-83, 10),
               (1, 6): Frac(-93, 10),
               (1, 7): Frac(-96, 10),
               (1, 8): Frac(-106, 10),
               (1, 9): Frac(-106, 10),
               (2, 2): Frac(-2),
               (2, 3): Frac(-35, 10),
               (2, 4): Frac(-59, 10),
               (2, 5): Frac(-73, 10),
               (2, 6): Frac(-83, 10),
               (2, 7): Frac(-86, 10),
               (2, 8): Frac(-96, 10),
               (2, 9): Frac(-96, 10),
               (3, 3): Frac(-15, 10),
               (3, 4): Frac(-39, 10),
               (3, 5): Frac(-53, 10),
               (3, 6): Frac(-63, 10),
               (3, 7): Frac(-66, 10),
               (3, 8): Frac(-76, 10),
               (3, 9): Frac(-76, 10),
               (4, 4): Frac(-24, 10),
               (4, 5): Frac(-38, 10),
               (4, 6): Frac(-48, 10),
               (4, 7): Frac(-51, 10),
               (4, 8): Frac(-61, 10),
               (4, 9): Frac(-61, 10),
               (5, 5): Frac(-14, 10),
               (5, 6): Frac(-24, 10),
               (5, 7): Frac(-27, 10),
               (5, 8): Frac(-37, 10),
               (5, 9): Frac(-37, 10),
               (6, 6): Frac(-1),
               (6, 7): Frac(-13, 10),
               (6, 8): Frac(-23, 10),
               (6, 9): Frac(-23, 10),
               (7, 7): Frac(-1),
               (7, 8): Frac(-22, 10),
               (7, 9): Frac(-23, 10),
               (8, 8): Frac(-19, 10),
               (8, 9): Frac(-24, 10),
               (9, 9): Frac(-16, 10)}
        self.assertEqual(ans, val)

    def test_dict_not_satisfied(self):
        sentences = u"the tourism initiative addresses this\
            for the first time".split()
        phrase_prob = {(1, 1): Frac(-1),
                       (2, 2): Frac(-2),
                       # lack one value
                       #(3, 3): Frac(-15, 10),
                       (4, 4): Frac(-24, 10),
                       (5, 5): Frac(-14, 10),
                       (6, 6): Frac(-1),
                       (7, 7): Frac(-1),
                       (8, 8): Frac(-19, 10),
                       (9, 9): Frac(-16, 10),
                       (3, 4): Frac(-4),
                       (5, 6): Frac(-25, 10),
                       (7, 8): Frac(-22, 10),
                       (6, 7): Frac(-13, 10),
                       (8, 9): Frac(-24, 10),
                       (5, 7): Frac(-27, 10),
                       (6, 8): Frac(-23, 10),
                       (7, 9): Frac(-23, 10),
                       (6, 9): Frac(-23, 10),
                       }
        self.assertRaises(ArgumentNotSatisfied,
                          _future_cost_estimate,
                          sentences,
                          phrase_prob)

    def test_create_estimate_dict(self):
        sentences = u"the tourism initiative addresses this\
            for the first time".split()
        phrase_prob = {(1, 1): Frac(-1),
                       (2, 2): Frac(-2),
                       # lack one value
                       #(3, 3): Frac(-15, 10),
                       (4, 4): Frac(-24, 10),
                       (5, 5): Frac(-14, 10),
                       #(6, 6): Frac(-1),
                       (7, 7): Frac(-1),
                       # lack one value
                       #(8, 8): Frac(-19, 10),
                       (9, 9): Frac(-16, 10),
                       (3, 4): Frac(-4),
                       (5, 6): Frac(-25, 10),
                       (7, 8): Frac(-22, 10),
                       (6, 7): Frac(-13, 10),
                       (8, 9): Frac(-24, 10),
                       (5, 7): Frac(-27, 10),
                       (6, 8): Frac(-23, 10),
                       (7, 9): Frac(-23, 10),
                       (6, 9): Frac(-23, 10),
                       }
        init_val = Frac(-100)
        ans = _create_estimate_dict(sentences,
                                    phrase_prob,
                                    init_val=init_val)
        correct = {(1, 1): Frac(-1),
                   (2, 2): Frac(-2),
                   # lack one value
                   (3, 3): init_val,
                   (4, 4): Frac(-24, 10),
                   (5, 5): Frac(-14, 10),
                   (6, 6): init_val,
                   (7, 7): Frac(-1),
                   # lack one value
                   (8, 8): init_val,
                   (9, 9): Frac(-16, 10),
                   (3, 4): Frac(-4),
                   (5, 6): Frac(-25, 10),
                   (7, 8): Frac(-22, 10),
                   (6, 7): Frac(-13, 10),
                   (8, 9): Frac(-24, 10),
                   (5, 7): Frac(-27, 10),
                   (6, 8): Frac(-23, 10),
                   (7, 9): Frac(-23, 10),
                   (6, 9): Frac(-23, 10),
                   }
        self.assertEqual(ans, correct)


if __name__ == '__main__':
    unittest.main()
