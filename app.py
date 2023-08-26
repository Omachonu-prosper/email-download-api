import os
import tempfile
from flask import Flask, jsonify
from pymongo import MongoClient
from flask_mail import Mail, Message
from dotenv import load_dotenv
import pandas as pd

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

# If we are working in a production environment (deployed state)
# the database to be used will be the mongodb atlas database
# else the local mongodb instance will be used
app_status = os.environ.get('APP_STATUS')
if app_status == 'production':
	db_username = os.environ['DATABASE_USER']
	db_passwd = os.environ['DATABASE_PASSWORD']
	db_url = os.environ['DATABASE_URL']
	uri = f"mongodb+srv://{db_username}:{db_passwd}@{db_url}"
else:
	uri = "mongodb://127.0.0.1:27017"

# pymongo configs and instantiation
client = MongoClient(uri)
db = client['plaschema']
passwords = db['passwords']


@app.route('/request/data/<int:limit>')
def retrieve_data(limit):
    data = passwords.find({}, {"_id": 0}).limit(limit)
    data = list(data)
    count = len(data)

    return jsonify({
        "message": "Data retrieved successfully",
        "count": count,
        "data": data,
        "status": True
    }), 200


@app.route('/request/data/<string:email>/<int:limit>')
def request_data_mail(email, limit):
    subject = 'Testing out some code'
    message_body = 'Body of the test message'

    data = passwords.find({}, {"_id": 0}).limit(limit)
    data = list(data)
    df = pd.DataFrame(data)
    
    # Save excel file temporarily on the server
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        filename = tmp.name
        filename = f"{filename}.xlsx"
        df.to_excel(filename, index=False)

    message = Message(subject=subject, recipients=[email], body=message_body)
    with app.open_resource(filename) as fp:
        message.attach("data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", fp.read())

    mail.send(message)
    return jsonify({
        'message': 'Mail sent successfully',
        'status': True,
        'data': None,
    }), 200
    

if __name__ == '__main__':
	if os.environ.get('APP_STATUS') == 'production':
		app.run()
	else:
		app.run(debug=True)