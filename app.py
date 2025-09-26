import os
import tempfile
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from datetime import datetime
from models import db, Document
from s3_client import upload_file_to_s3, delete_file_from_s3
from ai_service import extract_text_and_summarize, summarize_file
from dotenv import load_dotenv
load_dotenv()
import pytz

# Define the IST timezone
ist_timezone = pytz.timezone('Asia/Kolkata')

# # Get the current time in IST
# current_time_ist = datetime.now(ist_timezone)


app = Flask(__name__)
app.config.from_object("config.Config")
db.init_app(app)

# temp_path = r"C:\Users\ohkba\OneDrive\Documents\PROJECTS_GEN\project_assignment\temp_folder"

with app.app_context():
    db.create_all()

# ---------- Helper ----------
def paginate(query, page, per_page):
    return query.offset((page - 1) * per_page).limit(per_page).all()

# # ---------- Routes ---------- 
# @app.route("/documents", methods=["POST"])
# def create_document():
#     title = request.form.get("title")
#     description = request.form.get("description")
#     file = request.files.get("file")
#     if not file or not title:
#         return jsonify({"error": "title and file are required"}), 400

#     # Save locally for OCR
#     tmp_path = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
#     # tmp_path = r"C:\Users\ohkba\OneDrive\Documents\PROJECTS_GEN\project_assignment\temp_folder"
#     file.save(tmp_path)

#     # AI summary (OCR + Gemini)
#     ai_summary = extract_text_and_summarize(tmp_path)

#     # Upload to S3
#     s3_key = f"documents/{secure_filename(file.filename)}"
#     file_url = upload_file_to_s3(tmp_path, s3_key)

#     # Remove local file
#     if os.path.exists(tmp_path):
#         os.remove(tmp_path)

#     doc = Document(
#         title=title,
#         description=description,
#         file_url=file_url,
#         ai_summary=ai_summary,
#         # created_at=datetime.utcnow(),
#         # updated_at=datetime.utcnow()
#         created_at=datetime.now(ist_timezone),
#         updated_at=datetime.now(ist_timezone)
#     )
#     db.session.add(doc)
#     db.session.commit()
#     return jsonify(doc.to_dict()), 201

@app.route("/documents", methods=["POST"])
def create_document():
    title = request.form.get("title")
    description = request.form.get("description")
    file = request.files.get("file")
    if not file or not title:
        return jsonify({"error": "title and file are required"}), 400

    # Save locally for OCR or Gemini
    tmp_path = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
    file.save(tmp_path)

    try:
        # AI summary (PDF → OCR, Image → Gemini)
        ai_summary = summarize_file(tmp_path, file.filename)

        # Upload to S3
        s3_key = f"documents/{secure_filename(file.filename)}"
        file_url = upload_file_to_s3(tmp_path, s3_key)

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    doc = Document(
        title=title,
        description=description,
        file_url=file_url,
        ai_summary=ai_summary,
        # created_at=datetime.utcnow(),
        # updated_at=datetime.utcnow()
        created_at=datetime.now(ist_timezone),
        updated_at=datetime.now(ist_timezone)
    )
    db.session.add(doc)
    db.session.commit()
    return jsonify(doc.to_dict()), 201



@app.route("/documents", methods=["GET"])
def list_documents():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    search = request.args.get("search")

    query = Document.query
    if search:
        query = query.filter(Document.title.ilike(f"%{search}%"))
    docs = paginate(query.order_by(Document.created_at.desc()), page, per_page)
    return jsonify([d.to_dict() for d in docs])


@app.route("/documents/<string:doc_id>", methods=["GET"])
def get_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    return jsonify(doc.to_dict())


@app.route("/documents/<string:doc_id>", methods=["PUT"])
def update_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    title = request.form.get("title")
    description = request.form.get("description")
    file = request.files.get("file")

    if title:
        doc.title = title
    if description:
        doc.description = description

    if file:
        tmp_path = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
        file.save(tmp_path)
        # Optional re-summarize
        doc.ai_summary = extract_text_and_summarize(tmp_path)
        # Upload new file to S3
        s3_key = f"documents/{secure_filename(file.filename)}"
        file_url = upload_file_to_s3(tmp_path, s3_key)
        delete_file_from_s3(doc.file_url)
        doc.file_url = file_url
        os.remove(tmp_path)

    # doc.updated_at = datetime.utcnow()
    doc.updated_at = datetime.now(ist_timezone)
    db.session.commit()
    return jsonify(doc.to_dict())


@app.route("/documents/<string:doc_id>", methods=["DELETE"])
def delete_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    delete_file_from_s3(doc.file_url)
    db.session.delete(doc)
    db.session.commit()
    return jsonify({"message": "deleted"}), 200


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(debug=False, use_reloader=False)

