import unittest
from speechscore import align, evaluate, normalize, percentile

class ScoreTests(unittest.TestCase):
    def pair(self,r,h,**extra):
        return {'id':'x','reference':r,'hypothesis':h,**extra}
    def test_normalization(self):
        self.assertEqual(normalize('  HELLO, World!  '),'hello world')
    def test_unicode(self):
        self.assertEqual(normalize('ＡＢＣ Café'),'abc café')
    def test_edits(self):
        for a,b,op in [('a','b','substitute'),('a','','delete'),('','a','insert')]:
            self.assertEqual(align(a.split(),b.split())[0]['op'],op)
    def test_micro_average(self):
        rows=[self.pair('a','b'),{'id':'y','reference':'a b c','hypothesis':'a b c'}]
        self.assertEqual(evaluate(rows)['overall']['wer'],.25)
    def test_empty_reference(self):
        out=evaluate([self.pair('','hello')])['overall']
        self.assertIsNone(out['wer'])
        self.assertEqual(out['word_errors'],1)
    def test_insertions_can_exceed_one(self):
        self.assertEqual(evaluate([self.pair('a','a b c')])['overall']['wer'],2)
    def test_duplicate_ids(self):
        with self.assertRaises(ValueError): evaluate([self.pair('a','a')]*2)
    def test_invalid_latency(self):
        for value in [-1,float('nan'),float('inf'),True]:
            with self.assertRaises(ValueError): evaluate([self.pair('a','a',latency_ms=value)])
    def test_percentile(self):
        self.assertEqual(percentile([10,30,20],.95),30)
    def test_empty_dataset(self):
        self.assertIsNone(evaluate([])['overall']['cer'])
    def test_language_groups(self):
        self.assertIn('en', evaluate([self.pair('x','x',language='en')])['by_language'])
