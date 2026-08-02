from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import base64

class LLMClient(ABC):
    def encode_image(self, image_path: str) -> str:
        """Encode an image file to base64 string as PNG."""
        import logging
        from PIL import Image
        import io
        
        logger = logging.getLogger(__name__)
        
        try:
            # Load the image and convert to PNG format
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (PNG doesn't support all modes)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save to bytes in PNG format
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                png_data = buffer.getvalue()
                
                logger.debug(f"Converted {image_path} to PNG ({len(png_data)} bytes)")
                return base64.b64encode(png_data).decode('utf-8')
        except FileNotFoundError:
            logger.error(f"Image file not found: {image_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            raise

    @abstractmethod
    def generate(self,
        prompt: str,
        image_path: Optional[str] = None,
        stream: bool = False,
        model: str = "llama3.2-vision",
        temperature: float = 0.2,
        num_predict: int = 256) -> Dict[Any, Any]:
        pass
