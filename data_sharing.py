## Libraries imported:
## Flask is for creating web services
from flask import Flask, flash, request, redirect, render_template, url_for, jsonify,send_file
from flask_socketio import SocketIO, send, emit
## Used blockchain.py having blockchain class and block class
from blockchain import Blockchain
## Library to encrypt the file shared.
from cryptography.fernet import Fernet
## library to save the uploaded file.
import os

## Flask object and its config
app=Flask(__name__)
app.config['SECRET_KEY']='blockchain'
app.config['UPLOAD_FOLDER'] = "uploads"
app.config['KEY'] = 'TrKs5coimfg1tdC6tl2jIDszyLiOPrMpTY9q9dEC6RQ='

## Socket io used for socket connections
socketio = SocketIO(app)

## Object for block chain is created
blockchain = Blockchain()
## Fernet instance created for encryption and decryption.
fernet = Fernet(app.config['KEY'])


## web service for downloading a file.
@app.route('/download_file', methods = ['POST','GET'])
def download_file():
    try:
        ## get file key and file hash
        file_key = request.form['file_key']
        file_hash = request.form['file_hash']
        
    except Exception as e :
        render_template('download.html', message =str(e))
    
    msg="Downloading file "
    flag=0
    
    ## loop on all blocks present in blockchain
    for block in blockchain.chain:
        ## if key and block hash matches with entered hash then download file
        if block.blockData("key")==file_key and block.blockData("hash")==file_hash:
            ## Decrypt the file name
            dec_file = fernet.decrypt(bytes(block.blockData("file"),encoding='utf-8')).decode()
            msg=msg+ " "+ dec_file
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], dec_file)
            flag=1
            ## Download file
            return send_file(file_path, as_attachment=True)
    ## If block or entered file key not matches.
    if flag==0:
        msg="Key or Hash is not correct"
    ## return error message.
    return render_template('download.html' , message = msg)
 
## When download file link is clicked then display the download template
@app.route('/download', methods = ['GET'])
def download():
    return render_template('download.html',chain=blockchain.chain[::-1])
    
## When upload file link or home is clicked then display the upload template  
@app.route('/', methods = ['GET'])
def upload():
    return render_template('index.html',chain=blockchain.chain[::-1])

## When view shared file link is clicked then display all the blocks in the block chain.
@app.route('/viewchain', methods = ['GET'])
def viewchain():
    # print(blockchain.chain[1].blockData("file"))
    return render_template('viewchain.html',chain=blockchain.chain[::-1])

## When upload button is clicked on the upload template
@app.route('/upload_file', methods=['POST'])
def upload_file():
    ## get sender name
    sender = request.form['sender_name']
    ## get reciever name
    receiver = request.form['receiver_name']
    ## get file key
    file_key = request.form['file_key']
    ## get file name
    file_user=request.files['file']
    file_name = file_user.filename
    ## Create file name and path to save the file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    file_user.save(file_path)
    ## encrypt file name and same in data of the block
    hash_file_name = fernet.encrypt(str(file_name).encode())
    blockchain.add_file(sender, receiver, hash_file_name,file_key)
    return render_template('index.html' , message = "File succesfully uploaded",chain=blockchain.chain[::-1])

if __name__=='__main__':
    socketio.run(app, host = '127.0.0.1', port= 5111,debug=True)