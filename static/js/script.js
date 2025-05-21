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

    setTimeout(() => {
        if (popup) {
            popup.style.display = 'flex';
        }
    }, 700);

    //==============result section================
    const output = document.getElementById("prediction-output");
    // const ul = document.getElementById("confidence-list");
    // const votesBreak = document.getElementById("vote-breakdown");
    const adviceSec = document.getElementById("advice-section")
    const notesList = document.getElementById("notes-list");

    if (!output || !adviceSec || !notesList) {
        return;
    }

    const result   = sessionStorage.getItem("predictionResult");
    const notesStr  = sessionStorage.getItem("notes") || "[]";

    // render final line
    if (result == "Healthy") {
        output.innerText = "You are healthy!";
        output.classList.add("healthy");
    } else if (result == "Sick") {
        output.innerText = "You are sick!";
        output.classList.add("sick");
    } else {
        output.innerText = "No prediction available.";
    }

    let notes = []
    try {
        const parsed = JSON.parse(notesStr);
        // only accept it if it really is an array
        if (Array.isArray(parsed)) {
            notes = parsed;
        }
    } catch (e) {
        console.warn("Could not parse notes, defaulting to empty:", e);
    }

    if (notes.length) {
        adviceSec.classList.remove("hidden");
        notes.forEach(txt => {
            const li = document.createElement("li");
            li.innerText = txt;
            notesList.appendChild(li);
        }) 
    }
})

function closePrivacyNotice() {
    const popup = document.getElementById('privacy-popup');
    if (popup) {
        popup.style.display = 'none';
    }
}

function showErrorPopup() {
    const popup = document.getElementById("error-popup");
    if (popup) {
        popup.classList.remove("hidden");
        popup.style.display = 'flex';
    }
}

function closeErrorPopup() {
    const popup = document.getElementById("error-popup");
    if (popup) {
        popup.classList.add("hidden");
    }
}

function retry() {
    window.location.href = "/scan";
}


function handleFileUpload(e) {
    const file = e.target.files[0]
    if (!file) return;

    if (!["image/jpeg", "image/png"].includes(file.type)) {
        alert("Please upload a JPEG or PNG image.");
        e.target.value = "";
        return;
    }

    //remove scan container & show loader in place
    document.querySelector(".face-scan-container").remove();
    document.getElementById("privacy-popup")?.remove();
    document.querySelectorAll('body > p').forEach(el => el.remove());
    document.getElementById("camera-button")?.remove();

    const loader = document.createElement("div")
    loader.className = "analyzing-container";
    loader.innerHTML = `
        <div class="loader"></div>
        <h1>AI analysing...</h1>
        <p>It will take some time...</p>`;
    document.body.appendChild(loader)

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
        sessionStorage.setItem("notes", JSON.stringify(json.notes))

        setTimeout(() => {
        window.location.href = "/result";
        }, 1000);
    })
    .catch(err => {
        console.error("Prediction error:", err);
        showErrorPopup();
    });
}