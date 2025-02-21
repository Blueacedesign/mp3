flask
yt-dlp
moviepy
werkzeug
pillow
requests
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/[your-username]/video-to-mp3-converter.git
cd video-to-mp3-converter
```

2. Install dependencies using pip:
```bash
pip install flask yt-dlp moviepy werkzeug pillow requests
```

3. Set up environment variables:
```bash
export SESSION_SECRET=your_secret_key
```

4. Run the application:
```bash
python main.py
```

The application will be available at `http://localhost:5000`.

## Usage

1. Open the web interface in your browser
2. Paste a video URL (YouTube or other supported platforms)
3. Click "Convert to MP3"
4. Wait for the conversion to complete
5. Download your MP3 file with the original video title

## Deployment

To deploy this project to GitHub:

1. Create a new repository on GitHub.com
2. Run these commands in your terminal:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/[your-username]/video-to-mp3-converter.git
git push -u origin main