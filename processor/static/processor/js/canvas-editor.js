class CanvasEditor {
    constructor() {
        this.editorCanvas = document.getElementById('editor-canvas');
        this.backupCanvas = document.getElementById('backup-canvas');
        this.editorCtx = null;
        this.backupCtx = null;
        this.processedImage = null;
        this.originalImage = null;

        this.brushSize = 20;
        this.brushHardness = 100;
        this.brushMode = 'erase';
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

        const originalSrc = outputImage.dataset.originalSrc;
        if (!originalSrc) {
            console.error('No original image available');
            return;
        }

        this.processedImage = new Image();
        this.originalImage = new Image();

        let imagesLoaded = 0;
        const onImageLoad = () => {
            imagesLoaded++;
            if (imagesLoaded === 2) {
                this.setupCanvasDimensions();
                this.loadImageToCanvases();
                this.showEditor();
            }
        };

        this.processedImage.onload = onImageLoad;
        this.originalImage.onload = onImageLoad;

        this.processedImage.src = outputImage.src;
        this.originalImage.src = originalSrc;
    }

    setupCanvasDimensions() {
        const width = this.processedImage.naturalWidth;
        const height = this.processedImage.naturalHeight;

        this.editorCanvas.width = width;
        this.editorCanvas.height = height;
        this.backupCanvas.width = width;
        this.backupCanvas.height = height;
    }

    loadImageToCanvases() {
        this.editorCtx.drawImage(
            this.processedImage,
            0, 0,
            this.editorCanvas.width,
            this.editorCanvas.height
        );

        this.backupCtx.drawImage(
            this.originalImage,
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
        const brushHardnessSlider = document.getElementById('brush-hardness');
        const brushHardnessValue = document.getElementById('brush-hardness-value');

        brushSizeSlider.addEventListener('input', (e) => {
            this.brushSize = parseInt(e.target.value);
            brushSizeValue.textContent = this.brushSize;
        });

        brushHardnessSlider.addEventListener('input', (e) => {
            this.brushHardness = parseInt(e.target.value);
            brushHardnessValue.textContent = this.brushHardness;
        });

        const eraseModeBtn = document.getElementById('erase-mode-btn');
        const restoreModeBtn = document.getElementById('restore-mode-btn');
        const resetBtn = document.getElementById('reset-btn');
        const doneBtn = document.getElementById('done-btn');

        eraseModeBtn.addEventListener('click', () => this.setMode('erase'));
        restoreModeBtn.addEventListener('click', () => this.setMode('restore'));
        resetBtn.addEventListener('click', () => this.resetCanvas());
        doneBtn.addEventListener('click', () => this.closeEditor());
    }

    setMode(mode) {
        this.brushMode = mode;

        const eraseModeBtn = document.getElementById('erase-mode-btn');
        const restoreModeBtn = document.getElementById('restore-mode-btn');

        if (mode === 'erase') {
            eraseModeBtn.classList.add('active');
            restoreModeBtn.classList.remove('active');
        } else {
            restoreModeBtn.classList.add('active');
            eraseModeBtn.classList.remove('active');
        }
    }

    startDrawing(e) {
        this.isDrawing = true;
        const rect = this.editorCanvas.getBoundingClientRect();
        this.lastX = e.clientX - rect.left;
        this.lastY = e.clientY - rect.top;
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

        if (this.brushMode === 'erase') {
            this.editorCtx.globalCompositeOperation = 'destination-out';

            if (this.brushHardness === 100) {
                this.editorCtx.fillStyle = 'rgba(0, 0, 0, 1)';
                this.editorCtx.beginPath();
                this.editorCtx.arc(canvasX, canvasY, radius, 0, Math.PI * 2);
                this.editorCtx.fill();
            } else {
                const gradient = this.editorCtx.createRadialGradient(
                    canvasX, canvasY, radius * (this.brushHardness / 100),
                    canvasX, canvasY, radius
                );
                gradient.addColorStop(0, 'rgba(0, 0, 0, 1)');
                gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

                this.editorCtx.fillStyle = gradient;
                this.editorCtx.beginPath();
                this.editorCtx.arc(canvasX, canvasY, radius, 0, Math.PI * 2);
                this.editorCtx.fill();
            }

            this.editorCtx.globalCompositeOperation = 'source-over';
        } else if (this.brushMode === 'restore') {
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = this.editorCanvas.width;
            tempCanvas.height = this.editorCanvas.height;
            const tempCtx = tempCanvas.getContext('2d');

            if (this.brushHardness === 100) {
                tempCtx.fillStyle = 'rgba(0, 0, 0, 1)';
                tempCtx.beginPath();
                tempCtx.arc(canvasX, canvasY, radius, 0, Math.PI * 2);
                tempCtx.fill();
            } else {
                const gradient = tempCtx.createRadialGradient(
                    canvasX, canvasY, radius * (this.brushHardness / 100),
                    canvasX, canvasY, radius
                );
                gradient.addColorStop(0, 'rgba(0, 0, 0, 1)');
                gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

                tempCtx.fillStyle = gradient;
                tempCtx.beginPath();
                tempCtx.arc(canvasX, canvasY, radius, 0, Math.PI * 2);
                tempCtx.fill();
            }

            tempCtx.globalCompositeOperation = 'source-in';
            tempCtx.drawImage(this.backupCanvas, 0, 0);

            this.editorCtx.drawImage(tempCanvas, 0, 0);
        }
    }

    resetCanvas() {
        this.editorCtx.clearRect(0, 0, this.editorCanvas.width, this.editorCanvas.height);
        this.editorCtx.drawImage(
            this.processedImage,
            0, 0,
            this.editorCanvas.width,
            this.editorCanvas.height
        );
    }

    closeEditor() {
        const outputImage = document.getElementById('output-image');
        outputImage.src = this.editorCanvas.toDataURL('image/png');

        document.getElementById('canvas-editor').style.display = 'none';
        document.getElementById('result').style.display = 'block';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new CanvasEditor();
});