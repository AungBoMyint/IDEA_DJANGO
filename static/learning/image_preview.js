// image_preview.js
document.addEventListener("DOMContentLoaded", function () {
    const imageInput = document.querySelector('.image-preview input[type="file"]');
    const imagePreview = document.querySelector('.image-preview img');

    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function () {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    imagePreview.src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }
});
