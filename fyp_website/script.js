function startScan() {
    window.location.href = "face-scanningpage.html";
}

function accessCamera() {
    const video = document.getElementById('camera-activate');
    const overlayText = document.getElementById('overlay-text');

    navigator.mediaDevices.getUserMedia({video: true})
    .then(function(stream) {
        video.srcObject = stream;
        video.style.display = 'block';
        overlayText.style.display = 'none';
    })
    .catch(function(error) {
        console.error("Error accessing the camera: ", error);
        alert("Unable to access camera");
    })
}
document.addEventListener('DOMContentLoaded', function() {
    // file upload
    const uploadLink = document.getElementById('upload-link');
    const fileInput = document.getElementById('fileUpload');

    // camera capture
    const cameraButton = document.getElementById('camera-button');
    const video = document.getElementById('camera-activate');
    const overlayText = document.getElementById('overlay-text');
    
    

    if (uploadLink && fileInput) {
        uploadLink.addEventListener('click', function(event) {
            event.preventDefault();
            fileInput.click();
        })

        fileInput.addEventListener('change', function(event) {
            const file = event.target.files[0];

            if (file) {
                if (file.type === "image/jpeg" || file.type === "image/png") {
                    // const reader = new FileReader();
                    // reader.onload = function(e) {
                    //     previewImage.src = e.target.result;
                    //     previewImage.style.display = 'block';
                    alert("Image selected");
                    // reader.readAsDataURL(file);
                } else {
                    alert("Please upload a valid image (JPEG or PNG) ")
                    fileInput.value = "";
                }
            }
        })
    }
})

captueButton.addEventListener('click', function() {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    stream.getTracks().forEach(function(track) {
        track.stop();
    })

    video.style.display = 'none';
    canvas.style.display = 'block';
    captureButton.style.display = 'none';

    setTimeout(function() {
        window.location.href = "analysing-page.html";
    }, 1500);
})


// window.triggerUpload = function() {
//     document.getElementById('fileUpload').click();
// };

// document.getElementById('fileUpload').addEventListener('change', function(event) {
//     const file = event.target.files[0];

//     if (file) {
//         if (file.type === "image/jpeg" || file.type === "image/png") {
//             const reader = new FileReader();
//             reader.onload = function(e) {
//                 const previewImage = document.getElementById('preview-image');
//                 previewImage.src = e.target.result;
//                 previewImage.style.display = 'block';
//             }
//             reader.readAsDataURL(file);
//         } else {
//             alert("Please upload a valid image (JPEG or PNG) ")
//             event.target.value = "";
//         }
//     }
// })