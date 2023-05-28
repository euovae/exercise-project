function init() {

    buttonHandlerFunction = {
        
        classifyButton : undefined,
        startButton : undefined,
        clfResetState: undefined,
        
        getClfBTN : () => {
            return classifyButton;
        },
        
        getStartBTN : () => {
            return startButton;
        },

        getClfButtonDisabled : () => {
            return classifyButton.disabled;
        },

        getStartButtonDisabled : () => {
            return startButton.disabled;
        },

        disableClfBTN : () => {
            classifyButton.innerHTML = "...";
            classifyButton.disabled = true;
        },

        enableClfBTN : (str) => {
            classifyButton.innerHTML = str;
            classifyButton.disabled = false;            
        },

        disableStartBTN : () => {
            startButton.innerHTML = "...";
            startButton.disabled = true;
        },

        enableStartBTN : (str) => {
            startButton.innerHTML = str;
            startButton.disabled = false;
        },

        toggleClfResetState : () => {
            clfResetState = !clfResetState;
            if (clfResetState) {
                classifyButton.innerHTML = "Reset";
            }
            else {
                classifyButton.innerHTML = "Classify";
            }
            if (classifyButton.disabled) {
                classifyButton.disabled = false;
            } 
        },

        getClfResetState : () => {
            return clfResetState;
        },

        resetVariables : () => {
            classifyButton = document.getElementById("classifyButton");
            startButton = document.getElementById("startButton");
            buttonHandlerFunction.disableClfBTN();
            clfResetState = false;
        }
    }
    
    canvasAndCameraHandlerFunction = {

        camera : undefined,
        canvas : undefined,
        cameraFeedOn : undefined,

        getCanvas: () => {
            return canvas;
        },

        getCamera: () => {
            return camera;
        },

        getCameraFeedOn: () => {
            if (cameraFeedOn !== undefined){
                return cameraFeedOn;
            } else {
                return false;
            }
        },

        setCameraFeed: (bool) => {
            cameraFeedOn = bool;
        },

        clearCanvas: () => {
            canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height)
        },

        resetVariables : () => {
            camera = document.getElementById("webcam");
            canvas = document.getElementById("canvas");
            cameraFeedOn = false;
        }
    }

    bBoxHandlerFunction = {
        
        bBox : undefined,
        bBoxFound : undefined,
        predictions : undefined,
        detected : undefined,

        setBBox: (arg) => {
            bBox = arg;
        },

        getBBox: () => {
            return bBox;
        },

        setBBoxFound: (bool) => {
            bBoxFound = bool;
        },

        getBBoxFound: () => {
            return bBoxFound;
        },

        toggleDetected: () => {
            detected = !detected;
        },

        getDetected: () => {
            return detected;
        },

        setPreds: (arg) => {
            predictions = arg;
        },

        getPreds: () => {
            return predictions;
        },

        resetVariables : () => {
            bBox = undefined;
            bBoxFound = false;
            predictions = undefined;
            detected = false;
        },
    }

    const frameExtraction = {

        // Start the face recognition in the form of finding bounding boxes
        // by sending frames every 1s.
        extractFrames() {
            let data = canvasAndCamHandler.getCanvas().toDataURL('image/png');
            let formData = new FormData();
            formData.append('image', data)
            sendFrame(formData);
        },

        start() {
            this.intervalID = setInterval(this.extractFrames, 1000);
        },

        cancel() {
            clearInterval(this.intervalID);
        }
    }

    const canvasUpdater = {

        // Function to extract frames from the video element at 24fps
        // and insert the frame into canvas. 
        // Also draws new bounding boxes onto canvas.
        drawImageOnCanvas() {
            webcamFeed = canvasAndCamHandler.getCamera();
            canvas = canvasAndCamHandler.getCanvas();

            let mn = Math.min(webcamFeed.videoWidth, webcamFeed.videoHeight);
            let mx = Math.max(webcamFeed.videoWidth, webcamFeed.videoHeight);

            canvas.width = canvas.height = mn;
            canvas.getContext('2d').drawImage(webcamFeed, 
                0, 0,
                canvas.width, canvas.height,
            );

            if (bBoxHandler.getBBoxFound()){
                drawBBox();
            }
        },

        start() {
            // Calling the function above every 24fps
            this.intervalID = setInterval(this.drawImageOnCanvas, 41.666);
        },

        cancel() {
            clearInterval(this.intervalID);
        }
    }

    const buttonHandler = buttonHandlerFunction;
    const canvasAndCamHandler = canvasAndCameraHandlerFunction;
    const bBoxHandler = bBoxHandlerFunction;

    buttonHandler.resetVariables();
    canvasAndCamHandler.resetVariables();
    bBoxHandler.resetVariables();

    var localStream;

    // Function to start the camera and draw frames onto canvas.
    buttonHandler.getStartBTN().onclick = () => {
        if (!canvasAndCamHandler.getCameraFeedOn()) {
            buttonHandler.disableStartBTN()
            // Get the user's camera feed through HTML5.
            navigator.mediaDevices
            .getUserMedia({
                video: true,
                audio: false,
            })
            // Launch the camera and show it through the video element.
            // Extract and draw frames onto canvas and send them to the server.
            .then((stream) => {  
                localStream = stream;
                // Get the user's camera and play it through a <video> element.
                canvasAndCamHandler.getCamera().srcObject = localStream;
                canvasAndCamHandler.getCamera().addEventListener("loadedmetadata", () => {
                    canvasAndCamHandler.getCamera().play();
                })
                // Extract a frame from the <video> element at 24fps
                // and draw it onto the canvas.
                canvasUpdater.start();

                // Extract a frame from the <canvas> element at 1 fps
                // and send it to the server to receive a bounding box.
                frameExtraction.start();

                // Enable classification.
                buttonHandler.enableClfBTN("Classify")
                buttonHandler.enableStartBTN("Stop The Camera Feed")

                canvasAndCamHandler.setCameraFeed(true);
            
            }).catch((e) => {
                alert('Allow this website to use your camera.');
            });
        } else {
            localStream.getTracks().forEach(track => 
                track.stop()
            )
            reset()
        }

        function reset(){

            canvasAndCamHandler.getCamera().pause();
            canvasAndCamHandler.getCamera().currentTime = 0;

            canvasUpdater.cancel();
            frameExtraction.cancel();

            canvasAndCamHandler.clearCanvas();
            canvasAndCamHandler.setCameraFeed(false);
            buttonHandler.enableStartBTN("Start The Video Feed");

            buttonHandler.resetVariables();
            canvasAndCamHandler.resetVariables();
            bBoxHandler.resetVariables();
        }
    };

    // Start the classification process.
    buttonHandler.getClfBTN().onclick = function() {
    
        if (!buttonHandler.getClfResetState()) {
            // Let the user classify the image only if bounding boxes are detected.
            if (bBoxHandler.getBBoxFound()){

                // Grabbing the current frame from the canvas element
                // and encoding it into a base64 format through Data URLs.
                let data = canvasAndCamHandler.getCanvas().toDataURL('image/png');
                let formData = new FormData();
                formData.append('image', data)

                // Send the image to the server via a fetch() request.
                sendImageForClassification(formData);
                buttonHandler.disableClfBTN();
            } else {
                alert('Before classifying make sure the system has detected something')
            }
        } else {
            //det = false;
            bBoxHandler.toggleDetected();
            buttonHandler.toggleClfResetState();
        }
    }

    // Sending a frame and
    // requesting the bounding boxes for it from the server
    async function sendFrame(formData) {
        await fetch('/images', 
        {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(result => {
            res = JSON.parse(result)
            if(res.detection){
                bBoxHandler.setBBox(res);
                bBoxHandler.setBBoxFound(true);
            }
            else {
                bBoxHandler.setBBoxFound(false);
            }
        })
        .catch(error => console.log('error', error));
    }

    // Sending a frame and
    // requesting the age and gender predictions from the server
    async function sendImageForClassification(formData) {
        await fetch('/classify', 
        {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(result => {
            res = JSON.parse(result)
            if(res.detection){
                bBoxHandler.toggleDetected();
                bBoxHandler.setPreds(res);
                buttonHandler.toggleClfResetState();
            }
            else {
                bBoxHandler.toggleDetected();
                buttonHandler.enableClfBTN();
            }
        })
        .catch(error => console.log('error', error));
    }

    // Draw a rectangle on the canvas that surrounds the face
    // using the bounding boxes. Also draws the predictions by the models
    // after predictions were received from the server.
    function drawBBox(){
        dets = bBoxHandler.getDetected();
        preds = bBoxHandler.getPreds();
        bBox = bBoxHandler.getBBox();
        canvas = canvasAndCamHandler.getCanvas();
        canvas.getContext("2d").strokeStyle = "#7FFFD4";
        canvas.getContext("2d").strokeRect(
            bBox.x,
            bBox.y,
            bBox.w,
            bBox.h,
        )
        if (dets) {
            canvas.getContext("2d").font = "15px Arial";
            canvas.getContext("2d").strokeText(`Gender: ${preds.gender}, Age: ${preds.age}`, bBox.x+10, bBox.y+15);
        }
    }
}
init();