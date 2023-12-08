# app.py

from flask import Flask, render_template, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/form_app'
mongo = PyMongo(app)

@app.route('/')
def index():
    # Verifique se há um user_id na URL
    user_id = request.args.get('user_id')

    if user_id:
        # Se houver um user_id, renderize o formulário com os dados do usuário correspondente
        # Converta o user_id para ObjectId
        user_id_object = ObjectId(user_id)

        # Retrieve user data from MongoDB based on user_id
        user_data = mongo.db.users.find_one({'_id': user_id_object})

        if user_data:
            # Converta o ObjectId para string antes de renderizar o template
            user_data['_id'] = str(user_data['_id'])
            return render_template('form.html', user_data=user_data)
        else:
            return 'User not found', 404
    else:
        # Se não houver um user_id, renderize o formulário com campos vazios
        return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    form_data = {
        'user_id': get_next_user_id(),
        'firstName': request.form['firstName'],
        'lastName': request.form['lastName'],
        'birthday': request.form['birthday']
    }

    # Insert the form data into MongoDB
    mongo.db.users.insert_one(form_data)

    return 'Form submitted successfully!'

@app.route('/form')
def get_form_data():
    user_id = request.args.get('user_id')

    # Converta o user_id para ObjectId
    user_id_object = ObjectId(user_id) if user_id else None

    # Retrieve user data from MongoDB based on user_id
    user_data = mongo.db.users.find_one({'_id': user_id_object})

    # Converta o ObjectId para string antes de renderizar o template
    if user_data:
        user_data['_id'] = str(user_data['_id'])

        return render_template('form.html', user_data=user_data)
    else:
        return 'User not found', 404
    
@app.route('/form/all')
def get_all_form_data():
    users_data = list(mongo.db.users.find())
    if users_data:
        return render_template(users_data[0])
    else:
        return 'No users found', 404
    
def get_next_user_id():
    # Encontre o último usuário inserido e obtenha o próximo ID
    last_user = mongo.db.users.find_one(sort=[('user_id', -1)])
    return last_user['user_id'] + 1 if last_user else 1

# Adicione esta nova rota para obter o próximo user_id
@app.route('/next_user_id')
def get_next_user_id_route():
    next_user_id = get_next_user_id()
    return render_template({'next_user_id': next_user_id})

if __name__ == '__main__':
    app.run(debug=True)