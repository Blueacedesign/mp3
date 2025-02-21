import os
import sys
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

logger.debug(f"Python executable: {sys.executable}")
logger.debug(f"Python version: {sys.version}")
logger.debug(f"Python path: {sys.path}")
logger.debug(f"Current working directory: {os.getcwd()}")

try:
    import moviepy
    logger.debug(f"MoviePy version: {moviepy.__version__}")
    logger.debug(f"MoviePy location: {moviepy.__file__}")

    import moviepy.editor as mp
    logger.debug("MoviePy editor module successfully imported")

    # Create a simple test clip
    duration = 1  # seconds
    clip = mp.ColorClip(size=(1, 1), color=(0, 0, 0), duration=duration)
    logger.debug("Successfully created a test clip")

    # Clean up
    clip.close()
    logger.debug("Test completed successfully")

except Exception as e:
    logger.error(f"Error with MoviePy: {str(e)}")
    raise