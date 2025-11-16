"""
Unit tests for AnimationEngine
"""

import unittest
import time
from overlays.animation_engine import AnimationEngine, Animation, EasingType


class TestAnimation(unittest.TestCase):
    """Test Animation class"""
    
    def test_animation_creation(self):
        """Test creating an animation"""
        anim = Animation('test', duration=1.0, easing='linear')
        
        self.assertEqual(anim.name, 'test')
        self.assertEqual(anim.duration, 1.0)
        self.assertFalse(anim.is_active)
    
    def test_animation_start_stop(self):
        """Test starting and stopping animation"""
        anim = Animation('test', duration=1.0)
        
        anim.start()
        self.assertTrue(anim.is_active)
        
        anim.stop()
        self.assertFalse(anim.is_active)
    
    def test_animation_update(self):
        """Test animation update"""
        anim = Animation('test', duration=1.0)
        anim.start()
        
        # Update halfway through
        value = anim.update(0.5)
        
        self.assertGreater(value, 0)
        self.assertLess(value, 1.0)


class TestAnimationEngine(unittest.TestCase):
    """Test AnimationEngine functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = AnimationEngine()
    
    def test_engine_initialization(self):
        """Test engine initialization"""
        self.assertIsNotNone(self.engine.animations)
        self.assertEqual(self.engine.get_total_count(), 0)
    
    def test_register_animation(self):
        """Test registering animation"""
        anim = self.engine.register_animation('test', duration=1.0, easing='linear')
        
        self.assertIsNotNone(anim)
        self.assertEqual(self.engine.get_total_count(), 1)
    
    def test_start_animation(self):
        """Test starting animation"""
        self.engine.register_animation('test', duration=1.0)
        
        success = self.engine.start_animation('test')
        
        self.assertTrue(success)
        self.assertTrue(self.engine.is_animation_active('test'))
    
    def test_stop_animation(self):
        """Test stopping animation"""
        self.engine.register_animation('test', duration=1.0)
        self.engine.start_animation('test')
        
        success = self.engine.stop_animation('test')
        
        self.assertTrue(success)
        self.assertFalse(self.engine.is_animation_active('test'))
    
    def test_reset_animation(self):
        """Test resetting animation"""
        self.engine.register_animation('test', duration=1.0)
        self.engine.start_animation('test')
        self.engine.update(0.5)
        
        success = self.engine.reset_animation('test')
        
        self.assertTrue(success)
        anim = self.engine.animations['test']
        self.assertEqual(anim.elapsed_time, 0.0)
    
    def test_update_animations(self):
        """Test updating animations"""
        self.engine.register_animation('test', duration=1.0)
        self.engine.start_animation('test')
        
        self.engine.update(0.5)
        
        self.assertGreater(self.engine.total_time, 0)
    
    def test_get_animation_value(self):
        """Test getting animation value"""
        self.engine.register_animation('test', duration=1.0, easing='linear')
        self.engine.start_animation('test')
        self.engine.update(0.5)
        
        value = self.engine.get_animation_value('test')
        
        self.assertGreater(value, 0)
        self.assertLess(value, 1.0)
    
    def test_easing_linear(self):
        """Test linear easing"""
        value = self.engine.apply_easing(0.5, 'linear')
        self.assertEqual(value, 0.5)
    
    def test_easing_ease_in(self):
        """Test ease-in easing"""
        value = self.engine.apply_easing(0.5, 'ease_in')
        self.assertEqual(value, 0.25)  # 0.5^2
    
    def test_easing_ease_out(self):
        """Test ease-out easing"""
        value = self.engine.apply_easing(0.5, 'ease_out')
        self.assertEqual(value, 0.75)  # 0.5 * (2 - 0.5)
    
    def test_easing_ease_in_out(self):
        """Test ease-in-out easing"""
        value = self.engine.apply_easing(0.25, 'ease_in_out')
        self.assertEqual(value, 0.125)  # 2 * 0.25^2
    
    def test_easing_bounce(self):
        """Test bounce easing"""
        value = self.engine.apply_easing(0.5, 'bounce')
        self.assertGreater(value, 0)
        self.assertLessEqual(value, 1.0)
    
    def test_animation_looping(self):
        """Test animation looping"""
        self.engine.register_animation('test', duration=0.5, loop=True)
        self.engine.start_animation('test')
        
        # Update past duration
        self.engine.update(0.6)
        
        # Should still be active due to looping
        self.assertTrue(self.engine.is_animation_active('test'))
    
    def test_animation_reverse(self):
        """Test animation reverse"""
        self.engine.register_animation('test', duration=1.0, reverse=True)
        self.engine.start_animation('test')
        
        # Update past duration (needs to go through forward and reverse)
        self.engine.update(1.1)
        self.engine.update(1.1)
        
        # Should be complete after reverse
        self.assertTrue(self.engine.is_animation_complete('test'))
    
    def test_get_active_count(self):
        """Test getting active animation count"""
        self.engine.register_animation('test1', duration=1.0)
        self.engine.register_animation('test2', duration=1.0)
        
        self.engine.start_animation('test1')
        
        self.assertEqual(self.engine.get_active_count(), 1)
    
    def test_get_animation_info(self):
        """Test getting animation information"""
        self.engine.register_animation('test', duration=1.0, easing='linear')
        
        info = self.engine.get_animation_info('test')
        
        self.assertEqual(info['name'], 'test')
        self.assertEqual(info['duration'], 1.0)
        self.assertEqual(info['easing'], 'linear')


if __name__ == '__main__':
    unittest.main()
