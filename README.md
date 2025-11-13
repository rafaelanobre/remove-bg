# Django Background Remover

A simple, powerful web application that uses AI to automatically remove backgrounds from images.
Built with Django and powered by the rembg library for CPU-based background removal.

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Django](https://img.shields.io/badge/django-5.2.7+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Deployment](https://img.shields.io/badge/deployed-Google%20Cloud%20Run-4285F4.svg)

## Live Demo

**| [Try it live now!](https://remove-bg-1074036933469.us-central1.run.app)**

Upload an image → AI removes background → Download or copy the result!

> **Note:** First request after idle may take 10-15 seconds (cold start). Subsequent requests are fast!

## Features

### Core Features
- **AI-Powered** - Uses a neural network for accurate background removal with rembg
- **Three Upload Methods** - Click, Drag & Drop, or Paste (Ctrl+V) for flexible workflow
- **Instant Preview** - See results immediately with transparent background indicator
- **Download & Copy** - Save as PNG or copy directly to clipboard
- **Runs anywhere** - CPU-based processing, no GPU required
- **Production Ready** - Deployed on Google Cloud Run with CI/CD via GitHub Actions

### Canvas Retouch Editor
- **Professional Brush Tool** - Fine-tune AI results with precision editing
- **Dual Modes** - Erase unwanted pixels or restore original background
- **Configurable Brush** - Adjustable size (5-100px), hardness (0-100%), and opacity (10-100%)
- **Visual Cursor Preview** - See exact brush size and mode in real-time
- **Zoom & Pan Controls** - Precision editing with up to 400% zoom
- **Undo/Redo** - 20-level history for mistake-free editing
- **Keyboard Shortcuts** - Professional workflow with hotkeys
- **Touch Support** - Works on tablets and touch-enabled devices

## Tech Stack

**Backend:**
- Django 5.2.7+
- Python 3.12+
- rembg (AI background removal)
- Pillow (image processing)
- Celery 5.5+ (async task queue)
- Redis (message broker via Upstash)

**Frontend:**
- Vanilla JavaScript (ES6+)
- HTML5 & CSS3
- Font Awesome icons

**Infrastructure:**
- Google Cloud Run (serverless containers)
- Upstash Redis (managed Redis with TLS)
- GitHub Actions (CI/CD)

**Package Management:**
- uv (modern Python package manager)

## Installation

### Prerequisites

- Python 3.12 or higher
- pip or uv package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/rafaelanobre/remove-bg.git
   cd remove-bg
   ```

2. **Create virtual environment and install dependencies**

   Using `uv` (recommended):
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

   Or using traditional pip:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```

3. **Start the development server**
   ```bash
   python manage.py runserver
   ```

4. **Open your browser**

   Navigate to `http://127.0.0.1:8000/`

## Usage

### Basic Workflow

**Three Ways to Upload:**
1. **Click**: Click the drop zone to open file dialog and select an image
2. **Drag & Drop**: Drag an image file onto the purple drop zone
3. **Paste**: Copy an image (Ctrl+C) and paste anywhere (Ctrl+V)

**Processing:**
1. Upload triggers automatic background removal with AI
2. Wait a few seconds while the AI processes your image
3. View the result with transparent background (checkered pattern)
4. Click "Download" to save as PNG or "Copy Image" to copy to clipboard

**First-time use:** The AI model (~170MB) will be downloaded automatically on first run.

### Retouch Workflow (Optional)
After background removal, click **"Retouch"** to fine-tune the result:

1. **Choose Mode**: Select "Erase" to remove pixels or "Restore" to bring back original background
2. **Adjust Brush**: Use sliders to change brush size (5-100px), hardness (0-100%), and opacity (10-100%)
3. **Zoom & Pan**: Mouse wheel to zoom (up to 400%), Space+drag to pan around the canvas
4. **Paint**: Click and drag on the canvas to edit (brush cursor shows size and mode)
5. **Undo/Redo**: Use buttons or keyboard shortcuts (Ctrl+Z / Ctrl+Shift+Z)
6. **Reset**: Reload original AI result if needed
7. **Done**: Save your edits and return to download

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `E` | Switch to Erase mode |
| `R` | Switch to Restore mode |
| `[` | Decrease brush size (-5px) |
| `]` | Increase brush size (+5px) |
| `Shift + [` | Decrease hardness (-10%) |
| `Shift + ]` | Increase hardness (+10%) |
| `0-9` | Set opacity (10%-90%) |
| `Shift + 0` | Set opacity to 100% |
| `Ctrl + Z` | Undo last stroke |
| `Ctrl + Shift + Z` | Redo stroke |
| `Mouse Wheel` | Zoom in/out |
| `Space + Drag` | Pan canvas |

## Project Structure

```
remove-bg/
├── remove_bg/              # Django project configuration
│   ├── settings.py        # Project settings
│   ├── urls.py            # Main URL dispatcher
│   ├── wsgi.py            # WSGI entry point (for production deployment)
│   └── asgi.py            # ASGI entry point (not used - no async features)
├── processor/              # Django app for image processing
│   ├── views.py           # Request handlers
│   ├── urls.py            # App-specific URL routing
│   ├── models.py          # Database models (not used - stateless processing)
│   ├── apps.py            # App configuration
│   ├── admin.py           # Admin interface configuration (not used)
│   ├── tests.py           # Unit tests
│   └── static/            # App-specific static files
│       └── processor/
│           ├── css/       # Stylesheets
│           │   └── style.css
│           └── js/        # JavaScript files
│               ├── main.js          # Upload/download logic
│               └── canvas-editor.js # Canvas retouch tool
├── templates/             # Project-level HTML templates
│   └── processor/
│       └── home.html
├── manage.py              # Django CLI
├── pyproject.toml         # Dependencies (managed by uv)
└── db.sqlite3             # SQLite database (not used - stateless processing)
```

**Note:** This project uses stateless, in-memory image processing. No database storage is required, so `models.py`, `admin.py`, and `db.sqlite3` are currently unused but kept for potential future features. `asgi.py` is also unused as there are no async features (WebSockets, etc.). `wsgi.py` will be used for production deployment with gunicorn.

## Development

### Running Tests
```bash
python manage.py test
```

### Code Quality

**Check linting and formatting (what CI runs):**
```bash
uv run ruff check .
uv run ruff format --check .
```

**Auto-fix issues:**
```bash
uv run ruff check --fix .    # Fix linting issues
uv run ruff format .          # Auto-format code
```

### Code Style
This project follows PEP 8 guidelines and Django best practices.

## Deployment

This application is deployed on **Google Cloud Run** with automated CI/CD:

- **Platform**: Cloud Run (serverless containers)
- **Region**: us-central1
- **CI/CD**: GitHub Actions
- **Configuration**: 2GB RAM, 2 vCPU, 300s timeout
- **Scaling**: 0-2 instances (scales to zero when idle)
- **Cost**: Free tier covers 2M requests/month

### Deployment Pipeline

Every push to `main` triggers:
1. **Test Job**: Linting (ruff), formatting check, unit tests, Docker build
2. **Deploy Job**: Cloud Build → Artifact Registry → Cloud Run deployment

See `.github/workflows/deploy.yml` for the complete CI/CD configuration.

## Roadmap

**Phase 1-7: Complete ✅**
- [x] Basic upload and processing
- [x] Download and copy functionality
- [x] Loading indicators
- [x] Docker support with multi-stage builds
- [x] CI/CD pipeline via GitHub Actions
- [x] Production deployment on Google Cloud Run
- [x] **Canvas retouch tool with brush editor**
- [x] **Erase/Restore modes with configurable hardness**
- [x] **20-level undo/redo history**
- [x] **Keyboard shortcuts for professional workflow**
- [x] **Touch support for mobile/tablet devices**
- [x] **File validation and error handling**
- [x] **Three upload methods: Click, Drag & Drop, Paste (Ctrl+V)**
- [x] **Brush cursor preview with mode-based color coding**
- [x] **Variable opacity slider (10-100%)**
- [x] **Zoom/pan controls for precision editing (up to 400% zoom)**

**Phase 8: Background Task Queue (In Progress)**
- [x] **Async task processing with Celery + Upstash Redis**
- [x] **Instant API responses (~50ms instead of 3-5s)**
- [x] **Separate Celery worker service on Cloud Run**
- [x] **TLS-secured Redis connection with certificate verification**
- [x] **Frontend polling for task status updates**
- [x] **Automatic cleanup of old tasks and results**
- [ ] Error monitoring and alerting (Pending)

**Phase 9: Planned**
- [ ] Batch processing (multiple images)
- [ ] Infrastructure as Code with Terraform
- [ ] Rate limiting
- [ ] Performance monitoring dashboard

## License

MIT License

Copyright (c) 2025 Rafaela Nobre

**Acknowledgments:**

This project uses:
- [Django](https://www.djangoproject.com/), licensed under the BSD License.
- [rembg](https://github.com/danielgatis/rembg), which is licensed under the MIT License.
- [Pillow](https://python-pillow.github.io/), licensed under the PIL Software License.

