from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from typing import List
from loading import loading_graph

app = FastAPI()

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
        # Log file upload attempt
        try:
            # Process the file content directly
            answer = loading_graph(file)
            results.append(f"{file.filename}: {answer}")

        except Exception as e:
            # Log any exceptions
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
