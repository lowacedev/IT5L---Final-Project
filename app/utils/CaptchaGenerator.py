"""
CAPTCHA Generator Module
Generates CAPTCHA images for login verification
"""

import os
import random
import string
import logging
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Tuple

logger = logging.getLogger(__name__)


class CaptchaGenerator:
    """Generate and validate CAPTCHA codes"""
    
    # Configuration
    CAPTCHA_LENGTH = 6
    CAPTCHA_WIDTH = 300
    CAPTCHA_HEIGHT = 100
    BACKGROUND_COLOR = (255, 255, 255)  # White
    TEXT_COLOR = (50, 50, 50)  # Dark gray
    
    def __init__(self):
        """Initialize CAPTCHA generator"""
        self.current_code = None
        self.current_image_path = None
    
    @staticmethod
    def generate_code(length: int = CAPTCHA_LENGTH) -> str:
        """
        Generate a random CAPTCHA code.
        
        Args:
            length (int): Length of CAPTCHA code (default 6)
            
        Returns:
            str: Random CAPTCHA code (letters and numbers, excluding confusing chars)
        """
        # Exclude confusing characters: 0 (zero), O (oh), 1 (one), l (lowercase L), I (uppercase i)
        chars = string.ascii_uppercase + string.digits
        chars = chars.replace('0', '').replace('1', '').replace('O', '').replace('I', '')
        
        code = ''.join(random.choice(chars) for _ in range(length))
        return code
    
    def generate_image(self, code: str = None) -> Image.Image:
        """
        Generate CAPTCHA image with random code.
        
        Args:
            code (str): CAPTCHA code to display (generates new if not provided)
            
        Returns:
            Image.Image: PIL Image object
        """
        # Generate new code if not provided
        if code is None:
            code = self.generate_code()
        
        self.current_code = code
        
        # Create image with white background
        image = Image.new('RGB', (self.CAPTCHA_WIDTH, self.CAPTCHA_HEIGHT), self.BACKGROUND_COLOR)
        draw = ImageDraw.Draw(image)
        
        # Try to use a system font, fallback to default
        try:
            # Try common font paths
            font_paths = [
                "C:\\Windows\\Fonts\\arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/System/Library/Fonts/Helvetica.ttc"
            ]
            font = None
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, 50)
                    break
            
            if font is None:
                font = ImageFont.load_default()
        except Exception:
            font = ImageFont.load_default()
        
        # Add random lines for noise
        for _ in range(3):
            x1 = random.randint(0, self.CAPTCHA_WIDTH)
            y1 = random.randint(0, self.CAPTCHA_HEIGHT)
            x2 = random.randint(0, self.CAPTCHA_WIDTH)
            y2 = random.randint(0, self.CAPTCHA_HEIGHT)
            line_color = (random.randint(150, 220), random.randint(150, 220), random.randint(150, 220))
            draw.line([(x1, y1), (x2, y2)], fill=line_color, width=2)
        
        # Add random dots for noise
        for _ in range(20):
            x = random.randint(0, self.CAPTCHA_WIDTH)
            y = random.randint(0, self.CAPTCHA_HEIGHT)
            dot_color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
            draw.ellipse([(x, y), (x+2, y+2)], fill=dot_color)
        
        # Draw text with slight rotation for each character
        text_x = 20
        text_y = 25
        
        for char in code:
            # Random rotation angle
            angle = random.randint(-25, 25)
            
            # Create character image
            char_image = Image.new('RGBA', (60, 80), (255, 255, 255, 0))
            char_draw = ImageDraw.Draw(char_image)
            
            # Draw character with random color
            char_color = (random.randint(20, 80), random.randint(20, 80), random.randint(20, 80))
            char_draw.text((10, 15), char, font=font, fill=(*char_color, 255))
            
            # Rotate character
            char_image = char_image.rotate(angle, expand=True, fillcolor=(255, 255, 255, 0))
            
            # Paste onto main image
            image.paste(char_image, (text_x, text_y - 15), char_image)
            text_x += 40
        
        # Apply slight blur for anti-OCR effect
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return image
    
    def generate_image_file(self, code: str = None, output_path: str = None) -> str:
        """
        Generate CAPTCHA image and save to file.
        
        Args:
            code (str): CAPTCHA code (generates new if not provided)
            output_path (str): Path to save image (uses default if not provided)
            
        Returns:
            str: Path to saved image
        """
        try:
            # Generate image
            image = self.generate_image(code)
            logger.debug(f"Generated CAPTCHA image with code: {self.current_code}")
            
            # Determine output path
            if output_path is None:
                # Use project's temp directory instead of system temp
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                captcha_dir = os.path.join(project_root, '.captcha')
                os.makedirs(captcha_dir, exist_ok=True)
                output_path = os.path.join(captcha_dir, 'captcha_current.png')
            
            logger.debug(f"Saving CAPTCHA to: {output_path}")
            
            # Save image
            image.save(output_path, 'PNG')
            self.current_image_path = output_path
            logger.debug(f"CAPTCHA saved successfully: {output_path}")
            
            return output_path
        except Exception as e:
            logger.error(f"Error generating CAPTCHA image: {str(e)}", exc_info=True)
            raise
    
    def get_code_bytes(self, code: str = None) -> bytes:
        """
        Get CAPTCHA image as bytes.
        
        Args:
            code (str): CAPTCHA code (generates new if not provided)
            
        Returns:
            bytes: PNG image bytes
        """
        image = self.generate_image(code)
        
        # Save to bytes
        img_bytes = BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
    
    def validate(self, user_input: str) -> bool:
        """
        Validate user's CAPTCHA input.
        
        Args:
            user_input (str): User's CAPTCHA input
            
        Returns:
            bool: True if input matches, False otherwise
        """
        if self.current_code is None:
            return False
        
        # Case-insensitive comparison
        return user_input.strip().upper() == self.current_code.upper()
    
    def get_current_code(self) -> str:
        """Get the current CAPTCHA code"""
        return self.current_code
    
    def reset(self):
        """Reset CAPTCHA (clear current code)"""
        self.current_code = None
        self.current_image_path = None
