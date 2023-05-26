from flask import Flask, render_template, request, jsonify
import logging
import base64
import io
from PIL import Image
from classification import start_classification, start_bbox_detection

# Set-ExecutionPolicy Unrestricted -Scope Process
# env\Scripts\activate

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True

# Rendering the template of the landing page.
@app.route("/",)
def index():
    return render_template('index.html')

# Function for sending bounding boxes.
@app.route("/images", methods=['POST'])
def receiveBBox():
    # requesting a FormData object with an image
    encoded_image = request.form.get('image')
    # Removing the unneccesary header and decoding the received image
    decoded_image = base64.b64decode(encoded_image.replace("data:image/png;base64,",""))
    # Reading the bytes and opening the image using PIL
    bin_stream = io.BytesIO(decoded_image)
    pil_image = Image.open(bin_stream)

    # Sending jsonified bounding boxes detected from the image back to the client.
    response = start_bbox_detection(pil_image)
    if len(response) and response is not None:
        return jsonify(
            detection=True,
            x=int(response[0][0]),
            y=int(response[0][1]), 
            w=int(response[0][2]), 
            h=int(response[0][3]) 
        )  
    else:
        return jsonify(
            detection=False,
        )

@app.route("/classify", methods=['POST'])
def receiveClassification():
    # requesting a FormData object with an image
    encoded_image = request.form.get('image')
    # Removing the unneccesary header and decoding the received image
    decoded_image = base64.b64decode(encoded_image.replace("data:image/png;base64,",""))
    # Reading the bytes and opening the image using PIL
    bin_stream = io.BytesIO(decoded_image)
    pil_image = Image.open(bin_stream)

    # Sending predicted age range and gender from the image back to the client.
    response = start_classification(pil_image)
    print(response)
    if (response is not None):
        if (0 not in response):
            return jsonify(
                detection=True,
                gender=response[0],
                age=response[1],
        )  
        return jsonify(
            detection=False,
        )
    else:
        return jsonify(
            detection=False,
        )

if __name__ == "__main__":
    app.run(debug=True)