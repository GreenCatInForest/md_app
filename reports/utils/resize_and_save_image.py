from PIL import Image
import os
import logging

logger = logging.getLogger(__name__)

def resize_and_save_image(image_path, max_size=1500, quality=70, target_format=None):
    try:
        with Image.open(image_path) as img:
            original_format = img.format
            original_size = img.size
            width, height = original_size

            scaling_factor = min(max_size / float(max(width, height)), 1)

            if scaling_factor < 1:
                new_size = (int(width * scaling_factor), int(height * scaling_factor))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                logger.debug(f"Image resized from {original_size} to {new_size}")

            save_format = target_format.upper() if target_format else original_format

            new_file_path = os.path.splitext(image_path)[0] + f'.{save_format.lower()}'
            logger.debug(f"IMAGE RESIZING AND PATH: Image new file path {new_file_path}")

            if save_format == 'JPEG':
                img = img.convert('RGB')
                img.save(new_file_path, 'JPEG', quality=quality)
                logger.debug(f"IMAGE RESIZING: Image saved as JPEG with {quality}% quality at {new_file_path}")

            elif save_format == 'PNG':
                if img.mode != 'RGBA':
                    img = img.convert("RGBA")
                img.save(new_file_path, 'PNG', optimize=True)
                logger.debug(f"IMAGE RESIZING:Image saved as PNG at {new_file_path}")

            else:
                logger.error(f"Unsupported target format: {save_format}")
                return None

            if original_format != save_format:
                os.remove(image_path)
                logger.debug(f"Original image {image_path} removed after conversion to {save_format}.")
            logger.debug(f"IMAGE RESIZING AND PATH UTILS: Image path {new_file_path}, Image Type: {type(new_file_path)}")
            return new_file_path

    except Exception as e:
        logger.error(f"Error resizing image: {e} at {image_path}")
        return None