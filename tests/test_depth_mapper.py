import unittest
from dataclasses import replace
from config import ROOT,get_settings
from ganesha.path_loader import load_paths
from ganesha.depth_mapper import normalize,map_path,sample_polyline

class DepthTests(unittest.TestCase):
    def setUp(self):
        self.s=get_settings(); self.d=load_paths(ROOT/'data/ganesha_vector_data.json')
    def test_normalized_range_aspect_and_y_flip(self):
        self.assertEqual(normalize((500,600),1000,1200,self.s),(0,0))
        self.assertEqual(normalize((0,0),1000,1200,self.s),(-5,6))
        for p in self.d.paths:
            for x,y,z in map_path(p,self.d,self.s):
                self.assertLessEqual(abs(x),5); self.assertLessEqual(abs(y),6)
    def test_depth_category_and_determinism(self):
        p=self.d.paths[0]
        trunk=map_path(replace(p,category='trunk'),self.d,self.s)
        ear=map_path(replace(p,category='ears'),self.d,self.s)
        self.assertGreater(min(q[2] for q in trunk),max(q[2] for q in ear))
        self.assertEqual(trunk,map_path(replace(p,category='trunk'),self.d,self.s))
    def test_closed_seam_and_unknown_category(self):
        p=next(p for p in self.d.paths if p.is_closed)
        pts=map_path(p,self.d,self.s)
        self.assertAlmostEqual(pts[0][2],pts[-1][2])
        self.assertAlmostEqual(map_path(replace(p,category='unknown'),self.d,self.s)[0][2],0)
    def test_arc_length_sample(self):
        points=((0,0,0),(1,0,0),(1,3,0))
        self.assertEqual(sample_polyline(points,.5),(1,1,0))
        self.assertEqual(sample_polyline(points,1),points[-1])
