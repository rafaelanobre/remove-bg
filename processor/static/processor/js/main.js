const form = document.getElementById('upload-form');
const loading = document.getElementById('loading');
const result = document.getElementById('result');
const outputImage = document.getElementById('output-image');
const downloadBtn = document.getElementById('download-btn');
const copyBtn = document.getElementById('copy-btn');
const imageInput = document.getElementById('image-input');
const dropZone = document.getElementById('drop-zone');

let originalImageUrl = null;

const MAX_FILE_SIZE = window.UPLOAD_CONFIG.maxFileSize;
const ALLOWED_TYPES = window.UPLOAD_CONFIG.allowedTypes;
const ALLOWED_EXTENSIONS = window.UPLOAD_CONFIG.allowedExtensions;

function validateFile(file) {
    if (!file) {
        return { valid: false, error: 'Please select a file' };
    }

    if (file.size > MAX_FILE_SIZE) {
        const maxMB = MAX_FILE_SIZE / (1024 * 1024);
        return { valid: false, error: `File size exceeds ${maxMB}MB limit` };
    }

    if (!ALLOWED_TYPES.includes(file.type)) {
        return { valid: false, error: 'Invalid file type. Please upload JPG, PNG, or WebP images' };
    }

    const fileName = file.name.toLowerCase();
    const hasValidExtension = ALLOWED_EXTENSIONS.some(ext => fileName.endsWith(ext));
    if (!hasValidExtension) {
        return { valid: false, error: 'Invalid file extension. Allowed: .jpg, .jpeg, .png, .webp' };
    }

    return { valid: true };
}

function showError(message) {
    alert(message);
}

async function uploadFile(file) {
    const validation = validateFile(file);
    if (!validation.valid) {
        showError(validation.error);
        return;
    }

    dropZone.style.display = 'none';
    loading.style.display = 'block';
    result.style.display = 'none';

    const formData = new FormData();
    formData.append('image', file);
    formData.append('csrfmiddlewaretoken',
        document.querySelector('[name=csrfmiddlewaretoken]').value);

    try {
        const response = await fetch('', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const imageUrl = URL.createObjectURL(blob);

            outputImage.src = imageUrl;
            outputImage.dataset.originalSrc = originalImageUrl;
            loading.style.display = 'none';
            result.style.display = 'block';

            downloadBtn.onclick = () => {
                const a = document.createElement('a');
                a.href = imageUrl;
                a.download = 'background-removed.png';
                a.click();
            };

            copyBtn.onclick = async () => {
                try {
                    const item = new ClipboardItem({ 'image/png': blob });
                    await navigator.clipboard.write([item]);

                    copyBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
                    copyBtn.classList.add('copied');

                    setTimeout(() => {
                        copyBtn.innerHTML = '<i class="fa-solid fa-copy"></i> Copy Image';
                        copyBtn.classList.remove('copied');
                    }, 2000);
                } catch (error) {
                    console.error('Copy failed:', error);
                    alert('Failed to copy image. Please try download instead.');
                }
            };
        } else {
            try {
                const errorData = await response.json();
                showError(errorData.error || 'Error processing image. Please try again.');
            } catch {
                showError('Error processing image. Please try again.');
            }
            loading.style.display = 'none';
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Network error. Please check your connection and try again.');
        loading.style.display = 'none';
    }
}

imageInput.addEventListener('change', async () => {
    result.style.display = 'none';
    outputImage.src = '';

    const file = imageInput.files[0];
    if (file) {
        originalImageUrl = URL.createObjectURL(file);
        await uploadFile(file);
    }
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const file = imageInput.files[0];
    if (file) {
        originalImageUrl = URL.createObjectURL(file);
    }

    await uploadFile(file);
});

dropZone.addEventListener('click', () => {
    imageInput.click();
});

dropZone.addEventListener('dragenter', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', async (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');

    const file = e.dataTransfer.files[0];
    if (file) {
        originalImageUrl = URL.createObjectURL(file);
        await uploadFile(file);
    }
});

document.addEventListener('paste', async (e) => {
    const items = e.clipboardData.items;

    for (let item of items) {
        if (item.type.startsWith('image/')) {
            const file = item.getAsFile();
            if (file) {
                originalImageUrl = URL.createObjectURL(file);
                await uploadFile(file);
                break;
            }
        }
    }
});

const uploadAnotherBtn = document.getElementById('upload-another-btn');
uploadAnotherBtn.addEventListener('click', () => {
    result.style.display = 'none';

    dropZone.style.display = 'flex';

    imageInput.value = '';

    outputImage.src = '';

    originalImageUrl = null;
});