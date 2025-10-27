class CanvasEditor {
    constructor() {
        this.editorCanvas = document.getElementById('editor-canvas');
        this.backupCanvas = document.getElementById('backup-canvas');
        this.editorCtx = null;
        this.backupCtx = null;
        this.sourceImage = null;

        this.brushSize = 20;
        this.isDrawing = false;
        this.lastX = 0;
        this.lastY = 0;

        this.initializeCanvases();
        this.attachEventListeners();
    }

    initializeCanvases() {
        this.editorCtx = this.editorCanvas.getContext('2d', {
            willReadFrequently: true
        });
        this.backupCtx = this.backupCanvas.getContext('2d', {
            willReadFrequently: true
        });
    }

    attachEventListeners() {
        const retouchBtn = document.getElementById('retouch-btn');
        retouchBtn.addEventListener('click', () => this.openEditor());
    }

    openEditor() {
        const outputImage = document.getElementById('output-image');

        if (!outputImage.src) {
            console.error('No processed image available');
            return;
        }

        this.sourceImage = new Image();
        this.sourceImage.onload = () => {
            this.setupCanvasDimensions();
            this.loadImageToCanvases();
            this.showEditor();
        };
        this.sourceImage.src = outputImage.src;
    }

    setupCanvasDimensions() {
        const width = this.sourceImage.naturalWidth;
        const height = this.sourceImage.naturalHeight;

        this.editorCanvas.width = width;
        this.editorCanvas.height = height;
        this.backupCanvas.width = width;
        this.backupCanvas.height = height;
    }

    loadImageToCanvases() {
        this.editorCtx.drawImage(
            this.sourceImage,
            0, 0,
            this.editorCanvas.width,
            this.editorCanvas.height
        );

        this.backupCtx.drawImage(
            this.sourceImage,
            0, 0,
            this.backupCanvas.width,
            this.backupCanvas.height
        );
    }

    showEditor() {
        document.getElementById('result').style.display = 'none';
        document.getElementById('canvas-editor').style.display = 'block';
        this.attachCanvasEventListeners();
    }

    attachCanvasEventListeners() {
        this.editorCanvas.addEventListener('mousedown', (e) => this.startDrawing(e));
        this.editorCanvas.addEventListener('mousemove', (e) => this.draw(e));
        this.editorCanvas.addEventListener('mouseup', () => this.stopDrawing());
        this.editorCanvas.addEventListener('mouseout', () => this.stopDrawing());

        const brushSizeSlider = document.getElementById('brush-size');
        const brushSizeValue = document.getElementById('brush-size-value');

        brushSizeSlider.addEventListener('input', (e) => {
            this.brushSize = parseInt(e.target.value);
            brushSizeValue.textContent = this.brushSize;
        });
    }

    startDrawing(e) {
        this.isDrawing = true;
        const rect = this.editorCanvas.getBoundingClientRect();
        this.lastX = e.clientX - rect.left;
        this.lastY = e.clientY - rect.top;

        this.editorCtx.globalCompositeOperation = 'destination-out';
    }

    draw(e) {
        if (!this.isDrawing) return;

        const rect = this.editorCanvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        this.drawBrush(x, y);

        this.lastX = x;
        this.lastY = y;
    }

    stopDrawing() {
        this.isDrawing = false;
    }

    drawBrush(x, y) {
        const scaleX = this.editorCanvas.width / this.editorCanvas.getBoundingClientRect().width;
        const scaleY = this.editorCanvas.height / this.editorCanvas.getBoundingClientRect().height;

        const canvasX = x * scaleX;
        const canvasY = y * scaleY;
        const radius = this.brushSize;

        this.editorCtx.beginPath();
        this.editorCtx.arc(canvasX, canvasY, radius, 0, Math.PI * 2);
        this.editorCtx.fill();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new CanvasEditor();
});