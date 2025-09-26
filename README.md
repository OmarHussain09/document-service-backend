# Document Backend Service

This is a Flask-based backend service that provides CRUD operations for a "Document" resource. Each Document includes metadata (title, description) and an uploaded file (PDF or image). Files are stored in AWS S3 (or a compatible service like MinIO for local development). The service includes an AI-powered feature: automatic text extraction and summarization using OCR (via ocrmypdf for PDFs) and Google's Gemini LLM (via langchain-google-genai). Images are summarized directly using Gemini.

## Features
- **CRUD Operations**: Create, Read (list/single), Update, Delete Documents.
- **File Upload**: Supports PDFs and images (PNG, JPG, JPEG, WEBP). Files are uploaded to S3.
- **AI Summarization**: 
  - For PDFs: OCR is applied to extract text, then Gemini generates a 2-3 sentence summary.
  - For Images: Gemini directly analyzes the image and generates a 2-3 sentence summary.
- **Pagination and Search**: Document list endpoint supports pagination and title-based search.
- **Database**: SQLite (configurable via env) with timestamps in IST timezone.
- **Local S3 Compatibility**: Uses MinIO for development.

## Tech Stack
- Backend: Flask
- Database: SQLAlchemy (SQLite by default)
- File Storage: AWS S3 (via boto3, compatible with MinIO)
- AI/OCR: ocrmypdf, langchain-google-genai (Gemini LLM)
- Other: python-dotenv for env management, pytz for timezone handling

## Prerequisites
- Python 3.8+
- MinIO (for local S3 simulation) or real AWS S3 credentials.
- Google API Key for Gemini (free tier available at https://makersuite.google.com/).
- Optional: Docker for containerized deployment.

## Setup Instructions
1. Clone the repo:
   ```
   git clone https://github.com/yourusername/document-backend-service.git
   cd document-backend-service
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables: Copy `.env.example` to `.env` and fill in the values.
   - `DATABASE_URL`: e.g., `sqlite:///documents.db` (or PostgreSQL/MySQL URI for production).
   - `S3_BUCKET`: Your S3 bucket name (e.g., `mybucket`).
   - `S3_ENDPOINT`: S3 endpoint URL (e.g., `http://localhost:9000` for MinIO, or AWS endpoint).
   - `S3_ACCESS_KEY` and `S3_SECRET_KEY`: S3 credentials.
   - `GOOGLE_API_KEY`: Your Google API key for Gemini.
   - `OUTPUT_DIR`: Directory for temporary OCR output (default: `ocr_output`).

   Example `.env`:
   ```
   DATABASE_URL=sqlite:///documents.db
   S3_BUCKET=mybucket
   S3_ENDPOINT=http://localhost:9000
   S3_ACCESS_KEY=minioadmin
   S3_SECRET_KEY=minioadmin
   GOOGLE_API_KEY=your-google-api-key
   OUTPUT_DIR=ocr_output
   ```

4. Set up local MinIO (for development):
   - Install and run MinIO: Download from https://min.io/, or use Docker:
     ```
     docker run -p 9000:9000 -p 9001:9001 --name minio -e "MINIO_ROOT_USER=minioadmin" -e "MINIO_ROOT_PASSWORD=minioadmin" minio/minio server /data --console-address ":9001"
     ```
   - Create a bucket named `mybucket` via the MinIO console (http://localhost:9001).

5. Initialize the database:
   ```
   python init_db.py
   ```

## Running the Service Locally
1. Start the Flask app:
   ```
   python app.py
   ```
   The service will run on `http://localhost:5000` (default Flask port).

2. Test the endpoints using tools like Postman or curl. Examples:

   - **Create Document (POST /documents)**:
     - Form data: `title` (string), `description` (string, optional), `file` (PDF/image file).
     - Example curl:
       ```
       curl -X POST http://localhost:5000/documents -F "title=Sample Doc" -F "file=@/path/to/sample.pdf"
       ```

   - **List Documents (GET /documents)**:
     - Query params: `page` (int, default 1), `per_page` (int, default 10), `search` (string, optional).
     - Example: `http://localhost:5000/documents?page=1&per_page=5&search=sample`

   - **Get Single Document (GET /documents/<id>)**:
     - Example: `http://localhost:5000/documents/uuid-here`

   - **Update Document (PUT /documents/<id>)**:
     - Form data: `title` (optional), `description` (optional), `file` (optional new file).
     - If a new file is provided, it replaces the old one in S3 and re-summarizes.

   - **Delete Document (DELETE /documents/<id>)**:
     - Deletes from DB and S3.

