import os
import flask
from flask import Flask, request, jsonify
import shutil
from werkzeug.utils import secure_filename

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DATA_DIR, ollama_client, MODEL_NAME
from model import summarize_all_chunks_from_db
from filling_database import filling_database

app = Flask(__name__, static_folder='../app/build', static_url_path='/')

ALLOWED_EXTENSIONS = {'txt', 'md', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return app.send_static_file('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    question = data.get('question', '')
    summary = summarize_all_chunks_from_db(ollama_client, MODEL_NAME, batch_size=10)
    return jsonify({'answer': summary})

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'message': 'File type not supported.'}), 400
    for f in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
    from model import conn, cursor
    cursor.execute("TRUNCATE TABLE items;")
    conn.commit()
    filename = secure_filename(file.filename)
    save_path = os.path.join(DATA_DIR, filename)
    file.save(save_path)
    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'pdf':
        import PyPDF2
        text = ''
        with open(save_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text() or ''
        txt_path = os.path.splitext(save_path)[0] + '.txt'
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        filename = os.path.basename(txt_path)
    elif ext == 'docx':
        import docx
        doc = docx.Document(save_path)
        text = '\n'.join([p.text for p in doc.paragraphs])
        txt_path = os.path.splitext(save_path)[0] + '.txt'
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        filename = os.path.basename(txt_path)
    filling_database(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DATA_DIR, filename)
    summary = summarize_all_chunks_from_db(ollama_client, MODEL_NAME, batch_size=10)
    return jsonify({'message': 'File uploaded and processed.', 'summary': summary})

if __name__ == '__main__':
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    app.run(host='localhost', port=5000)

