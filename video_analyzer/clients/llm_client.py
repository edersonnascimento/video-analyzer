from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import base64

class LLMClient(ABC):
    def encode_image(self, image_path: str) -> str:
        """Encode an image file to base64 string."""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                logger.debug(f"Read {len(image_data)} bytes from {image_path}")
                return base64.b64encode(image_data).decode('utf-8')
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
