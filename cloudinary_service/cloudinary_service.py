import cloudinary

# import json
import os

# ==============================
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv

load_dotenv()


# Upload a file to Cloudinary and return its URL
def cloudinary_upload(file):
    cloudinary.config(
        cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
        api_key=os.environ.get("CLOUDINARY_API_KEY"),
        api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
        secure=True,
    )
    upload_result = cloudinary.uploader.upload(file)
    return upload_result["secure_url"]


# Set configuration parameter: return "https" URLs by setting secure=True
# ==============================
config = cloudinary.config(secure=True)

# Log the configuration
# ==============================
print(
    "****1. Set up and configure the SDK:****\nCredentials: ",
    config.cloud_name,
    config.api_key,
    "\n",
)
