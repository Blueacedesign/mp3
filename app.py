import os
import sys
import logging
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import tempfile
import threading
import time
from urllib.parse import urlparse
import yt_dlp
import re

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

def sanitize_filename(title):
    """Sanitize the title to be a valid filename"""
    # Remove invalid filename characters
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    # Remove or replace other problematic characters
    title = title.replace('\n', ' ').replace('\r', ' ')
    # Limit length
    return title[:100].strip()

def is_youtube_url(url):
    try:
        parsed_url = urlparse(url)
        return any(domain in parsed_url.netloc for domain in ['youtube.com', 'youtu.be'])
    except:
        return False

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def download_youtube_video(url, output_path):
    try:
        logger.debug(f"Attempting to download from URL: {url}")

        # Extract filename without extension from output_path
        output_dir = os.path.dirname(output_path)
        output_filename = os.path.splitext(os.path.basename(output_path))[0]

        video_title = None

        def get_video_info(d):
            nonlocal video_title
            if d.get('status') == 'finished':
                if not video_title and d.get('info_dict', {}).get('title'):
                    video_title = sanitize_filename(d['info_dict']['title'])
                logger.debug(f"Download progress: {d.get('status', 'unknown')}")
            else:
                logger.debug(f"Download progress: {d.get('status', 'unknown')}")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(output_dir, f'{output_filename}.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
            'extract_audio': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [get_video_info],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                logger.debug("Starting download with yt-dlp")
                ydl.download([url])
                # The actual output file will have .mp3 extension
                final_output = os.path.join(output_dir, f'{output_filename}.mp3')
                if os.path.exists(final_output):
                    logger.debug(f"Download completed successfully: {final_output}")
                    return True, final_output, video_title, None
                else:
                    logger.error("Output file not found after download")
                    return False, None, None, "Failed to create output file"
            except Exception as e:
                error_msg = str(e)
                if "Private video" in error_msg:
                    return False, None, None, "This video is private and cannot be accessed."
                elif "Sign in" in error_msg:
                    return False, None, None, "This video requires authentication. Please try a different video."
                elif "unavailable" in error_msg:
                    return False, None, None, "This video is unavailable. It might have been removed or is region-restricted."
                else:
                    logger.error(f"Download error: {error_msg}")
                    return False, None, None, "Failed to download the video. Please try a different video or check if it's available."

    except Exception as e:
        logger.error(f"Unexpected error during download: {str(e)}")
        return False, None, None, f"An unexpected error occurred: {str(e)}"

# Store conversion progress and file paths
conversion_progress = {}
output_files = {}
output_titles = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert_url():
    if 'url' not in request.json:
        return jsonify({'error': 'No URL provided'}), 400

    url = request.json['url']
    if not is_valid_url(url):
        return jsonify({'error': 'Invalid URL format'}), 400

    try:
        # Create temporary directory for processing
        temp_dir = tempfile.mkdtemp()
        task_id = str(int(time.time()))
        output_path = os.path.join(temp_dir, 'output')

        # Set initial progress
        conversion_progress[task_id] = 0

        def process_download():
            try:
                # Download and convert to MP3
                success, file_path, title, error = download_youtube_video(url, output_path)
                if success:
                    conversion_progress[task_id] = 100
                    output_files[task_id] = file_path
                    output_titles[task_id] = title or 'converted_audio'
                    logger.debug(f"Saved output file path: {file_path} for task {task_id}")
                else:
                    conversion_progress[task_id] = -1
                    logger.error(f"Download failed: {error}")
            except Exception as e:
                conversion_progress[task_id] = -1
                logger.error(f"Process error: {str(e)}")

        # Start processing in background
        thread = threading.Thread(target=process_download)
        thread.start()

        return jsonify({
            'task_id': task_id,
            'message': 'Conversion started'
        })

    except Exception as e:
        logger.error(f"Process error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/progress/<task_id>')
def get_progress(task_id):
    progress = conversion_progress.get(task_id, 0)
    return jsonify({'progress': progress})

@app.route('/download/<task_id>')
def download_file(task_id):
    try:
        file_path = output_files.get(task_id)
        if not file_path:
            logger.error(f"No file path found for task {task_id}")
            return jsonify({'error': 'File not found'}), 404

        if os.path.exists(file_path):
            title = output_titles.get(task_id, 'converted_audio')
            logger.debug(f"Sending file: {file_path}")
            return send_file(
                file_path,
                as_attachment=True,
                download_name=f'{title}.mp3',
                mimetype='audio/mpeg'
            )
        else:
            logger.error(f"File not found at path: {file_path}")
            return jsonify({'error': 'File not found'}), 404

    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)