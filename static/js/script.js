function startScan() {
    window.location.href = "/scan";
}

document.addEventListener('DOMContentLoaded', function() {
    // file upload
    const uploadLink = document.getElementById('upload-link');
    const fileInput = document.getElementById('fileUpload');
    const cameraButton = document.getElementById('camera-button');
    const popup = document.getElementById('privacy-popup');
    
    if (uploadLink && fileInput) {
        uploadLink.addEventListener('click', e => {
            e.preventDefault();
            fileInput.click();
        });
        fileInput.addEventListener("change", handleFileUpload);
    }

    // camera activate & capture
    if (cameraButton) {
        const video = document.getElementById('camera-activate');
        const overlayText = document.getElementById('overlay-text');
        const canvas = document.getElementById('photo-canvas');
        let stream, isCameraActive = false;

        cameraButton.addEventListener('click', () => {
            if (!isCameraActive) {
                navigator.mediaDevices.getUserMedia({video: true})
                .then(s => {
                    stream = s;
                    video.srcObject = s;
                    video.style.display = 'block';
                    overlayText.style.display = 'none';
                    isCameraActive = true;
                })
                .catch(err => {
                    console.error("Error accessing camera", error);
                    alert("Unable to access camera");
                })
            } else {
                const context = canvas.getContext('2d');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                context.drawImage(video, 0, 0, canvas.width, canvas.height);

                stream.getTracks().forEach(t => t.stop());

                video.style.display = 'none';
                canvas.style.display = 'none';
                cameraButton.style.display = 'none';
                overlayText.style.display  = "none";

                canvas.toBlob(blob => {
                    const file = new File([blob], "capture.png", { type: "image/png" });
                    handleFileUpload({ target: { files: [file] } });
                  }, "image/png");
            }
        })
    }

    if (popup) {
        popup.style.display = 'flex';
    }
})

function closePrivacyNotice() {
    const popup = document.getElementById('privacy-popup');
    if (popup) {
        popup.style.display = 'none';
    }
}

function handleFileUpload(e) {
    const file = e.target.files[0]
    if (!file) return;

    if (!["image/jpeg", "image/png"].includes(file.type)) {
        alert("Please upload a JPEG or PNG image.");
        e.target.value = "";
        return;
      }

      // show spinner overlay on THIS page
    document.querySelector(".face-scan-container").style.display = "none";
    document.getElementById("privacy-popup")?.remove();
    const loader = document.createElement("div");
    loader.className = "analyzing-container";
    loader.innerHTML =
        `<div class="loader"></div>
        <h1>AI analysing…</h1>
        <p>It will take some time...</p>`;
    document.body.appendChild(loader);

    
      // show loading page
    //   window.location.href = "/analyse";
    
      const data = new FormData();
      data.append("file", file);
    
      fetch("/predict", { method: "POST", body: data })
        .then(res =>
            res.json().then(payload => {
            if (!res.ok) {
                // server sent you a JSON error message
                throw new Error(payload.error || `${res.status} ${res.statusText}`);
            }
            return payload;
            })
        )
        .then(json => {
          // stash & go to results
          sessionStorage.setItem("predictionResult",    json.result);
          sessionStorage.setItem("predictionConfidence",json.confidence);
          sessionStorage.setItem("votes", JSON.stringify(json.votes));
          sessionStorage.setItem("confidences", JSON.stringify(json.confidences));

          window.location.href = "/result";
        })
        .catch(err => {
          console.error("Prediction error:", err);
          alert("Something went wrong while predicting the image.");
        });
}

// function accessCamera() {
//     const video = document.getElementById('camera-activate');
//     const overlayText = document.getElementById('overlay-text');

//     navigator.mediaDevices.getUserMedia({video: true})
//     .then(function(stream) {
//         video.srcObject = stream;
//         video.style.display = 'block';
//         overlayText.style.display = 'none';
//     })
//     .catch(function(error) {
//         console.error("Error accessing the camera: ", error);
//         alert("Unable to access camera");
//     })
// }

// document.getElementById('fileUpload').addEventListener('change', e => {
//     const file = e.target.files[0];
//     if (!file) return;
//     if (!['image/jpeg','image/png'].includes(file.type)) {
//       alert("upload jpeg/png");
//       return;
//     }
//     // show loading page
//     window.location.href = "/analyse";
  
//     const data = new FormData();
//     data.append("file", file);
  
//     fetch("/predict", { method:"POST", body:data })
//       .then(r => r.json())
//       .then(d => {
//         sessionStorage.setItem("predictionResult",    d.result);
//         sessionStorage.setItem("predictionConfidence", d.confidences[d.result.toLowerCase()] );
//         window.location.href = "/result";
//       })
//       .catch(err => {
//         console.error(err);
//         alert("Prediction failed");
//       });
//   });
  



// captureButton.addEventListener('click', function() {
//     const context = canvas.getContext('2d');
//     canvas.width = video.videoWidth;
//     canvas.height = video.videoHeight;
//     context.drawImage(video, 0, 0, canvas.width, canvas.height);

//     stream.getTracks().forEach(function(track) {
//         track.stop();
//     })

//     video.style.display = 'none';
//     canvas.style.display = 'block';
//     captureButton.style.display = 'none';

//     setTimeout(function() {
//         window.location.href = "analysing-page.html";
//     }, 1500);
// })


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