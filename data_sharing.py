from flask import Flask, flash, request, redirect, render_template, url_for, jsonify
from flask_socketio import SocketIO, send, emit
from blockchain import Blockchain
from cryptography.fernet import Fernet
import os

app=Flask(__name__)
app.config['SECRET_KEY']='blockchain'
app.config['UPLOAD_FOLDER'] = "uploads"
app.config['DOWNLOAD_FOLDER'] = "downloads"
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['KEY'] = 'TrKs5coimfg1tdC6tl2jIDszyLiOPrMpTY9q9dEC6RQ='
app.config['BUFFER_SIZE'] = 64 * 1024
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

socketio = SocketIO(app)

blockchain = Blockchain()
fernet = Fernet(app.config['KEY'])





@app.route('/download_file', methods = ['POST','GET'])
def download_file():
    file_key = request.form['file_key']
    file_hash = request.form['file_hash']
    msg="Downloading file "
    for block in blockchain.chain:
        if block.blockData("key")==file_key:
            dec_file = fernet.decrypt(file_hash).decode()
            msg=msg+ dec_file
        else:
            msg="Key or Hash is not correct"
    return render_template('download.html' , message = msg)
 
@app.route('/download', methods = ['GET'])
def download():
    return render_template('download.html',chain=blockchain.chain[::-1])
    
    
@app.route('/', methods = ['GET'])
def upload():
    return render_template('index.html',chain=blockchain.chain[::-1])
    
@app.route('/viewchain', methods = ['GET'])
def viewchain():
    # print(blockchain.chain[1].blockData("file"))
    return render_template('viewchain.html',chain=blockchain.chain[::-1])


@app.route('/upload_file', methods=['POST'])
def upload_file():
    sender = request.form['sender_name']
    receiver = request.form['receiver_name']
    file_key = request.form['file_key']
    file_user=request.files['file']
    file_name = file_user.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    file_user.save(file_path)
    hash_file_name = fernet.encrypt(str(file_path).encode())
    blockchain.add_file(sender, receiver, hash_file_name,file_key)
    return render_template('index.html' , message = "File succesfully uploaded")

if __name__=='__main__':
    socketio.run(app, host = '127.0.0.1', port= 5111,debug=True)