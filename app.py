from flask import Flask, render_template, request
import boto3
import os
from PIL import Image
import io

app = Flask(_name_)

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
                MaxFaces=100
            )

            # ✅ Extract results + image URL
            for match in response["FaceMatches"]:
                key = match["Face"]["ExternalImageId"]

                image_url = f"https://{BUCKET}.s3.ap-south-1.amazonaws.com/all/all/{key}"

                results.append({
                    "name": key,
                    "url": image_url
                })

        except Exception as e:
            error = str(e)

    return render_template("index.html", results=results, error=error)


# ✅ FIX (बहुत जरूरी)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
