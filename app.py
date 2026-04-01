from flask import Flask, render_template, request
import boto3
import os
from PIL import Image
import io

app = Flask(__name__)

# ✅ AWS credentials from environment (SAFE)
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY")
AWS_REGION = "ap-south-1"

# ✅ AWS clients
rekognition = boto3.client(
    "rekognition",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

BUCKET = "amzn-saar-mumbai"
COLLECTION_ID = "face_collection"


@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    error = None

    if request.method == "POST":
        try:
            file = request.files["image"]

            if file.filename == "":
                error = "No file selected"
                return render_template("index.html", results=results, error=error)

            # ✅ Fix RGBA issue
            img = Image.open(file)
            if img.mode == "RGBA":
                img = img.convert("RGB")

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG")
            image_bytes = buffer.getvalue()

            # ✅ Search face in Rekognition
            response = rekognition.search_faces_by_image(
                CollectionId=COLLECTION_ID,
                Image={"Bytes": image_bytes},
                FaceMatchThreshold=80,
                MaxFaces=100  # 🔥 unlimited jaisa (max 100)
            )

            # ✅ Extract results
            for match in response["FaceMatches"]:
                face_id = match["Face"]["ExternalImageId"]
                results.append(face_id)

        except Exception as e:
            error = str(e)

    return render_template("index.html", results=results, error=error)


if _name_ == "_main_":
    app.run(host="0.0.0.0", port=5000)