import os

from flask import Flask, flash, redirect, render_template, request, send_file
from werkzeug.utils import secure_filename                                                                                                                                                                                                                                                                                                                                              
import decrypter as dec
import divider as dv
import encrypter as enc
import restore as rst
import tools
from flask import jsonify
import joblib

UPLOAD_FOLDER = './uploads/'
UPLOAD_KEY = './key/'
ALLOWED_EXTENSIONS = set(['pem'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_KEY'] = UPLOAD_KEY
app.secret_key = os.urandom(24)
#port = int(os.getenv('PORT', 8000))
model = joblib.load('predictive_encryption_model.pkl')

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def start_encryption():
    dv.divide()
    tools.empty_folder('uploads')
    enc.encrypter()
    return render_template('success.html')


def start_decryption():
    dec.decrypter()
    tools.empty_folder('key')
    rst.restore()
    return render_template('restore_success.html')

def check_sensitive_data(file_path):
    try:
        # Read the content of the uploaded file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            file_content = file.read()

        # Predict using the loaded model
        is_sensitive = model.predict([file_content])  # Use predict function on file content

        # The 'is_sensitive' variable will contain the prediction result
        return bool(is_sensitive[0])
    except Exception as e:
        print(f"Error reading file: {e}")
        return False  # Return False if there's an error



@app.route('/return-key')
def return_key():
    print("reached")
    list_directory = tools.list_dir('key')
    filename = './key/' + list_directory[0]
    print(filename)
    return send_file(filename, download_name="My_Key.pem", as_attachment=True)


@app.route('/return-file/')
def return_file():
    list_directory = tools.list_dir('restored_file')
    filename = './restored_file/' + list_directory[0]
    print("****************************************")
    print(list_directory[0])
    print("****************************************")
    return send_file(filename, download_name=list_directory[0], as_attachment=True)


@app.route('/download/')
def downloads():
    return render_template('download.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/upload')
def call_page_upload():
    return render_template('upload.html')


@app.route('/home')
def back_home():
    tools.empty_folder('key')
    tools.empty_folder('restored_file')
    return render_template('index.html')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data', methods=['GET', 'POST'])
def upload_file():
    tools.empty_folder('uploads')
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return 'NO FILE SELECTED'
        
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            if check_sensitive_data(file_path):
                return render_template('confirm.html', filename=filename)
            else:
                return start_encryption()
        
        return 'Invalid File Format !'
    
    return render_template('success.html')  # Return a response for GET requests




@app.route('/confirm-upload/<filename>', methods=['GET', 'POST'])
def confirm_upload(filename):
    if request.method == 'POST':
        return start_encryption()  # Proceed with encryption upon confirmation
    return render_template('confirm.html', filename=filename)




@app.route('/download_data', methods=['GET', 'POST'])
def upload_key():
    tools.empty_folder('key')
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return 'NO FILE SELECTED'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_KEY'], file.filename))
            return start_decryption()
        return 'Invalid File Format !'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
    # app.run()
