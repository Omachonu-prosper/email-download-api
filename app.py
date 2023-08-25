import os
import tempfile
from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_mail import Mail, Message
from dotenv import load_dotenv
from openpyxl import Workbook

load_dotenv()

app = Flask(__name__)

# Flask-Mail config
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# pymongo configs and instantiation
client = MongoClient('mongodb://localhost:27017')
db = client['plaschema']
passwords = db['passwords']

# Openpyxl instantiation
wb = Workbook()

@app.route('/retrieve/data')
def retrieve_data():
    data = passwords.find({}, {"_id": 0}).limit(100)
    data = list(data)
    count = len(data)

    return jsonify({
        "message": "Data retrieved successfully",
        "count": count,
        "data": data,
        "status": True
    }), 200


@app.route('/request/data/mail')
def request_data_mail():
    recipient = 'omachonucodes@gmail.com'
    subject = 'Testing out some code'
    message_body = 'Body of the test message'

    data = passwords.find({}, {"_id": 0})
    data = list(data)
    sheet = wb.active
    heading = ['rank', 'password']
    sheet.append(heading)

    for obj in data:
        row = [
            obj.get('rank'),
            obj.get('password')
        ]
        sheet.append(row)

    # Save excel file temporarily on the server
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        filename = tmp.name
        wb.save(filename)

    message = Message(subject=subject, recipients=[recipient], body=message_body)
    with app.open_resource(filename) as fp:
        message.attach(f"{filename}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", fp.read())

    mail.send(message)
    return jsonify({
        'message': 'Mail sent successfully',
        'status': True,
        'data': None,
    }), 200
    

if __name__ == '__main__':
    app.run(debug=True)