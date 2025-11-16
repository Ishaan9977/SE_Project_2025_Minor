"""
Animation Engine for ADAS Overlays
Provides smooth animations with easing functions
"""

import time
import logging
from typing import Dict, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class EasingType(Enum):
    """Easing function types"""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"


class Animation:
    """Single animation instance"""
    
    def __init__(self, name: str, duration: float, easing: str = "linear", 
                 loop: bool = False, reverse: bool = False):
        """
        Initialize animation
        
        Args:
            name: Animation name
            duration: Duration in seconds
            easing: Easing function type
            loop: Whether to loop the animation
            reverse: Whether to reverse after completion
        """
        self.name = name
        self.duration = duration
        self.easing = easing
        self.loop = loop
        self.reverse = reverse
        
        self.start_time = None
        self.elapsed_time = 0.0
        self.is_active = False
        self.is_complete = False
        self.is_reversed = False
        self.current_value = 0.0
    
    def start(self):
        """Start the animation"""
        self.start_time = time.time()
        self.elapsed_time = 0.0
        self.is_active = True
        self.is_complete = False
        self.current_value = 0.0
    
    def update(self, delta_time: float) -> float:
        """
        Update animation and return current value
        
        Args:
            delta_time: Time since last update
            
        Returns:
            Current animation value (0.0 to 1.0)
        """
        if not self.is_active:
            return self.current_value
        
        self.elapsed_time += delta_time
        
        # Calculate progress (0.0 to 1.0)
        if self.duration > 0:
            progress = min(self.elapsed_time / self.duration, 1.0)
        else:
            progress = 1.0
        
        # Reverse if needed
        if self.is_reversed:
            progress = 1.0 - progress
        
        # Store current value
        self.current_value = progress
        
        # Check if complete
        if self.elapsed_time >= self.duration:
            if self.reverse and not self.is_reversed:
                # Start reverse
                self.is_reversed = True
                self.elapsed_time = 0.0
            elif self.loop:
                # Restart
                self.elapsed_time = 0.0
                self.is_reversed = False
            else:
                # Complete
                self.is_complete = True
                self.is_active = False
        
        return self.current_value
    
    def stop(self):
        """Stop the animation"""
        self.is_active = False
    
    def reset(self):
        """Reset the animation"""
        self.elapsed_time = 0.0
        self.is_active = False
        self.is_complete = False
        self.is_reversed = False
        self.current_value = 0.0


class AnimationEngine:
    """
    Animation engine for managing multiple animations with easing functions
    """
    
    def __init__(self):
        """Initialize animation engine"""
        self.animations: Dict[str, Animation] = {}
        self.last_update_time = time.time()
        self.total_time = 0.0
        
        logger.info("Animation Engine initialized")
    
    def register_animation(self, name: str, duration: float, easing: str = "linear",
                          loop: bool = False, reverse: bool = False) -> Animation:
        """
        Register a new animation
        
        Args:
            name: Unique animation name
            duration: Duration in seconds
            easing: Easing function type
            loop: Whether to loop
            reverse: Whether to reverse after completion
            
        Returns:
            Created Animation instance
        """
        animation = Animation(name, duration, easing, loop, reverse)
        self.animations[name] = animation
        
        logger.debug(f"Animation registered: {name} (duration: {duration}s, easing: {easing})")
        
        return animation
    
    def start_animation(self, name: str) -> bool:
        """
        Start an animation
        
        Args:
            name: Animation name
            
        Returns:
            True if started, False if not found
        """
        if name in self.animations:
            self.animations[name].start()
            logger.debug(f"Animation started: {name}")
            return True
        else:
            logger.warning(f"Animation not found: {name}")
            return False
    
    def stop_animation(self, name: str) -> bool:
        """
        Stop an animation
        
        Args:
            name: Animation name
            
        Returns:
            True if stopped, False if not found
        """
        if name in self.animations:
            self.animations[name].stop()
            logger.debug(f"Animation stopped: {name}")
            return True
        else:
            logger.warning(f"Animation not found: {name}")
            return False
    
    def reset_animation(self, name: str) -> bool:
        """
        Reset an animation
        
        Args:
            name: Animation name
            
        Returns:
            True if reset, False if not found
        """
        if name in self.animations:
            self.animations[name].reset()
            logger.debug(f"Animation reset: {name}")
            return True
        else:
            logger.warning(f"Animation not found: {name}")
            return False
    
    def update(self, delta_time: Optional[float] = None):
        """
        Update all active animations
        
        Args:
            delta_time: Time since last update (auto-calculated if None)
        """
        if delta_time is None:
            current_time = time.time()
            delta_time = current_time - self.last_update_time
            self.last_update_time = current_time
        
        self.total_time += delta_time
        
        # Update all animations
        for animation in self.animations.values():
            if animation.is_active:
                animation.update(delta_time)
    
    def get_animation_value(self, name: str) -> float:
        """
        Get current animation value with easing applied
        
        Args:
            name: Animation name
            
        Returns:
            Eased animation value (0.0 to 1.0)
        """
        if name not in self.animations:
            logger.warning(f"Animation not found: {name}")
            return 0.0
        
        animation = self.animations[name]
        raw_value = animation.current_value
        
        # Apply easing function
        eased_value = self.apply_easing(raw_value, animation.easing)
        
        return eased_value
    
    def apply_easing(self, t: float, easing_type: str) -> float:
        """
        Apply easing function to value
        
        Args:
            t: Input value (0.0 to 1.0)
            easing_type: Easing function type
            
        Returns:
            Eased value (0.0 to 1.0)
        """
        # Clamp input
        t = max(0.0, min(1.0, t))
        
        if easing_type == "linear" or easing_type == EasingType.LINEAR.value:
            return t
        
        elif easing_type == "ease_in" or easing_type == EasingType.EASE_IN.value:
            # Quadratic ease in
            return t * t
        
        elif easing_type == "ease_out" or easing_type == EasingType.EASE_OUT.value:
            # Quadratic ease out
            return t * (2.0 - t)
        
        elif easing_type == "ease_in_out" or easing_type == EasingType.EASE_IN_OUT.value:
            # Quadratic ease in-out
            if t < 0.5:
                return 2.0 * t * t
            else:
                return -1.0 + (4.0 - 2.0 * t) * t
        
        elif easing_type == "bounce" or easing_type == EasingType.BOUNCE.value:
            # Bounce ease out
            if t < (1.0 / 2.75):
                return 7.5625 * t * t
            elif t < (2.0 / 2.75):
                t -= (1.5 / 2.75)
                return 7.5625 * t * t + 0.75
            elif t < (2.5 / 2.75):
                t -= (2.25 / 2.75)
                return 7.5625 * t * t + 0.9375
            else:
                t -= (2.625 / 2.75)
                return 7.5625 * t * t + 0.984375
        
        elif easing_type == "elastic" or easing_type == EasingType.ELASTIC.value:
            # Elastic ease out
            if t == 0.0 or t == 1.0:
                return t
            
            import math
            p = 0.3
            s = p / 4.0
            return math.pow(2.0, -10.0 * t) * math.sin((t - s) * (2.0 * math.pi) / p) + 1.0
        
        else:
            logger.warning(f"Unknown easing type: {easing_type}, using linear")
            return t
    
    def is_animation_active(self, name: str) -> bool:
        """Check if animation is active"""
        if name in self.animations:
            return self.animations[name].is_active
        return False
    
    def is_animation_complete(self, name: str) -> bool:
        """Check if animation is complete"""
        if name in self.animations:
            return self.animations[name].is_complete
        return False
    
    def get_animation_info(self, name: str) -> Optional[Dict]:
        """Get animation information"""
        if name not in self.animations:
            return None
        
        anim = self.animations[name]
        return {
            'name': anim.name,
            'duration': anim.duration,
            'easing': anim.easing,
            'loop': anim.loop,
            'reverse': anim.reverse,
            'is_active': anim.is_active,
            'is_complete': anim.is_complete,
            'current_value': anim.current_value,
            'elapsed_time': anim.elapsed_time
        }
    
    def clear_completed_animations(self):
        """Remove completed non-looping animations"""
        to_remove = []
        for name, anim in self.animations.items():
            if anim.is_complete and not anim.loop:
                to_remove.append(name)
        
        for name in to_remove:
            del self.animations[name]
            logger.debug(f"Removed completed animation: {name}")
    
    def get_active_count(self) -> int:
        """Get number of active animations"""
        return sum(1 for anim in self.animations.values() if anim.is_active)
    
    def get_total_count(self) -> int:
        """Get total number of registered animations"""
        return len(self.animations)
