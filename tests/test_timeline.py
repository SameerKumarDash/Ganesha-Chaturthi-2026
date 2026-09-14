import unittest
from dataclasses import replace
from config import ROOT,get_settings
from ganesha.path_loader import load_paths
from animation.timeline import PHASES,frame,validate_phases,schedule

class TimelineTests(unittest.TestCase):
    def test_phase_order(self):
        self.assertTrue(validate_phases())
        with self.assertRaises(ValueError): validate_phases([PHASES[0],replace(PHASES[1],start=3)])
    def test_frames(self):
        self.assertEqual(frame(8,get_settings()),481)
        self.assertEqual(frame(8,get_settings(animation_speed=2)),241)
    def test_schedule_complete_sequential(self):
        paths=load_paths(ROOT/'data/ganesha_vector_data.json').paths
        slots=schedule(paths)
        self.assertEqual([s.path.id for s in slots],[p.id for p in paths])
        self.assertTrue(all(s.start<s.end for s in slots))
        self.assertTrue(all(a.end<=b.start for a,b in zip(slots,slots[1:])))
        self.assertAlmostEqual(slots[-1].end,58)
    def test_external_order_preserved(self):
        paths=load_paths(ROOT/'data/ganesha_vector_data.json').paths
        reverse=tuple(reversed(paths))
        self.assertEqual([s.path.id for s in schedule(reverse)],[p.id for p in reverse])
