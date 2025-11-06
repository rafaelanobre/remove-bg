const form = document.getElementById('upload-form');
const loading = document.getElementById('loading');
const result = document.getElementById('result');
const outputImage = document.getElementById('output-image');
const downloadBtn = document.getElementById('download-btn');
const copyBtn = document.getElementById('copy-btn');
const imageInput = document.getElementById('image-input');

let originalImageUrl = null;

imageInput.addEventListener('change', () => {
    result.style.display = 'none';
    outputImage.src = '';

    const file = imageInput.files[0];
    if (file) {
        originalImageUrl = URL.createObjectURL(file);
    }
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    loading.style.display = 'block';
    result.style.display = 'none';

    const formData = new FormData(form);

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
                a.href = outputImage.src;
                a.download = 'background-removed.png';
                a.click();
            };

            copyBtn.onclick = async () => {
                try {
                    const response = await fetch(outputImage.src);
                    const blob = await response.blob();
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
            alert('Error processing image. Please try again.');
            loading.style.display = 'none';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error processing image. Please try again.');
        loading.style.display = 'none';
    }
});