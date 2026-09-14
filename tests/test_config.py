import unittest
from config import PRESETS,get_settings

class ConfigTests(unittest.TestCase):
    def test_presets(self):
        previous=0
        for name in PRESETS:
            s=get_settings(name)
            self.assertGreater(s.star_count,previous); previous=s.star_count
            self.assertEqual(s.fps,60)
            self.assertTrue(s.enable_galaxies)
    def test_invalid(self):
        with self.assertRaises(ValueError): get_settings('impossible')
        for overrides in ({'animation_speed':0},{'animation_speed':float('nan')},{'fps':-1},{'particle_count':-1}):
            with self.assertRaises(ValueError): get_settings(**overrides)
    def test_overrides(self):
        s=get_settings('medium',render_width=800,enable_nebula=False)
        self.assertEqual(s.star_count,2500)
        self.assertEqual(s.render_width,800); self.assertFalse(s.enable_nebula)
