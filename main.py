from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from typing import List
import os
from loading import loading_graph

app = FastAPI()

# Create the "Temporary" folder if it doesn't exist
TEMP_DIR = "Temporary"
os.makedirs(TEMP_DIR, exist_ok=True)

# Home page
@app.get("/", response_class=HTMLResponse)
async def home_page():
    return """
    <html>
        <head>
            <title>Please upload document</title>
        </head>
        <body>
            <h1>Please upload document</h1>
            <form action="/upload" method="get">
                <button type="submit">Upload</button>
            </form>
        </body>
    </html>
    """

# Upload page
@app.get("/upload", response_class=HTMLResponse)
async def upload_page():
    return """
    <html>
        <head>
            <title>Upload Document</title>
        </head>
        <body>
            <h1>Upload Documents</h1>
            <form action="/upload_file" method="post" enctype="multipart/form-data">
                <input type="file" name="files" multiple>
                <button type="submit">Upload</button>
            </form>
        </body>
    </html>
    """

# File upload handler
@app.post("/upload_file")
async def upload_file(files: List[UploadFile] = File(...)):
    results = []

    for file in files:
        try:
            # Save the uploaded file to the "Temporary" folder
            file_location = os.path.join(TEMP_DIR, file.filename)
            with open(file_location, "wb") as f:
                f.write(await file.read())

            # Pass the file path to the loading_graph function
            answer = loading_graph(file_location)
            results.append(f"{file.filename}: {answer}")

        except Exception as e:
            results.append(f"{file.filename}: Error - {e}")

    return HTMLResponse(f"""
    <html>
        <head>
            <title>Files Uploaded</title>
        </head>
        <body>
            <h1>Files Uploaded Successfully</h1>
            <ul>
                {"".join(f"<li>{result}</li>" for result in results)}
            </ul>
            <a href="/">Go to Home Page</a>
        </body>
    </html>
    """)

