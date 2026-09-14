import json
from pathlib import Path
import tempfile
import unittest
import warnings
from config import ROOT
from ganesha.path_loader import load_paths,extract_points

class PathLoaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT/'output').mkdir(exist_ok=True)  # git-ignored, so absent on a fresh clone

    def load(self,obj):
        with tempfile.TemporaryDirectory(dir=ROOT/'output') as folder:
            p=Path(folder)/'fixture.json'; p.write_text(json.dumps(obj))
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                return load_paths(p)
    def test_bundled_json(self):
        d=load_paths(ROOT/'data/ganesha_vector_data.json')
        self.assertEqual(len(d.paths),119)
        self.assertEqual(d.diagnostics,())
    def test_bad_entries_skip_without_losing_good(self):
        good={'id':'good','points':[[0,0],[3,4]],'step_order':1}
        d=self.load([None,{}, {'points':[[0,0],['nan',3]]},
                     {'points':[[0,0],[.001,.001]]}, {'points':[[0,0],[1,1]],'width':-1},good])
        self.assertEqual(len(d.paths),1)
        self.assertEqual(len(d.diagnostics),5)
    def test_sort_stable(self):
        def p(i,s): return {'id':i,'step_order':s,'points':[[0,0],[2,3]]}
        d=self.load([p('z',2),p('b',1),p('a',1)])
        self.assertEqual([p.id for p in d.paths],['b','a','z'])
    def test_cubic_and_duplicate_points(self):
        pts=extract_points({'bezier_segments':[[[0,0],[0,3],[3,3],[3,0]]]})
        self.assertEqual(pts[0],(0,0)); self.assertEqual(pts[-1],(3,0))
        self.assertAlmostEqual(pts[8][1],2.25)
        self.assertEqual(extract_points({'points':[[0,0],[0,0],{'x':3,'y':4}]}),[(0,0),(3,4)])
    def test_closed_and_metadata(self):
        d=self.load([{'points':[[0,0],[3,0],[3,4]],'is_closed':True,'is_filled':True,'fill_color':'gold'}])
        self.assertEqual(d.paths[0].points[0],d.paths[0].points[-1])
        self.assertTrue(d.paths[0].is_filled)
    def test_invalid_root_empty_and_missing(self):
        for obj in ([],{},'bad',{'canvas':{'width':0},'paths':[]}):
            with self.assertRaises(ValueError): self.load(obj)
        with self.assertRaisesRegex(ValueError,'missing'): load_paths(ROOT/'data/does-not-exist.json')
    def test_malformed_json(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'output') as folder:
            p=Path(folder)/'bad.json'; p.write_text('{broken')
            with self.assertRaisesRegex(ValueError,'Invalid vector JSON'): load_paths(p)
    def test_disconnected_cubics_rejected(self):
        with self.assertRaisesRegex(ValueError,'disconnected'):
            extract_points({'bezier_segments':[[[0,0],[1,0],[2,0],[3,0]],[[7,0],[8,0],[9,0],[10,0]]]})
