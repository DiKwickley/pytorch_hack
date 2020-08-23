from flask import Flask, render_template, url_for, flash,session
from flask import request, redirect
import os
import json
from datetime import datetime, timedelta, date
from flask_pymongo import PyMongo





app = Flask(__name__)





app.config["MONGO_URI"] = "mongodb://aniket:Aniketsprx077@cluster0-shard-00-00-uugt8.mongodb.net:27017,cluster0-shard-00-01-uugt8.mongodb.net:27017,cluster0-shard-00-02-uugt8.mongodb.net:27017/hackathon?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true&w=majority"
mongo = PyMongo(app)



app.secret_key = 'aniket'									
app.permanent_session_lifetime = timedelta(days = 28)

@app.route('/')
def main():
	return render_template('index.html')



@app.route('/signup')
def signup():
	return render_template("signup.html")

@app.route('/handle_signup', methods=['POST','GET'])
def handle_signup():

	if request.method == 'POST':
		email = request.form['email']
		name = request.form['name']
		password = request.form['password']
		
		if 'remember' in request.form:
			remember = request.form['remember']
		else:
			remember = 'off'
		# remember has two values on and off

		print("email: ", email)
		print("name: ", name)
		print("password: ", password)
		print("remember: ", remember)
		user = {
		'email': email,
		'name' : name,
		'password' : password
		}

		if mongo.db.user.find_one({"email" : email}) != None:
			#account exits
			return redirect(url_for("signup", msg='email_exists', **request.args))
		else:
			#account does not exits
			mongo.db.user.insert_one(user)
			#account created

			
			session['user'] = email

			if remember == 'off':
				session['forget'] = True

			return redirect(url_for('account'))

	else:
		return redirect(url_for('signup'))


@app.route('/login')
def login():
	if 'user' in session:
		return redirect(url_for('account'))
	else:
		return render_template('login.html')

@app.route('/handle_login', methods=['POST', 'GET'])
def handle_login():

	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']


		user = mongo.db.user.find_one({'email' : email})
		print('USER: ', user)
		if user == None:
			#no such email
			return redirect(url_for('login', msg='no_such_email', **request.args))
		else:
			if user['password'] != password:
				#wrong password
				return redirect(url_for('login', msg='wrong_password', **request.args))
			else:
				#login success
				print("login success")
				session['user'] = email
				return redirect(url_for('account'))


	
@app.route('/account')
def account():

	if 'user' in session:
		email = session['user']
		if 'forget' in session:
			session.pop('forget', None)
		data = mongo.db.user.find_one({"email" : email})
		del data['_id']
		print("DATA: ",data)
		return render_template('account.html', data=json.dumps(data))
	else:
		return redirect(url_for('main'))
		

@app.route('/annotation', method=['POST', 'GET'])
def annotation():
	if request.method == 'POST':
		# check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        else:
        	file.save(os.path.join('./static/upload/', file.filename))
        	return render_template('annotation.html',res=json.dumps({'file': '../static/upload/'+file.filename, 'email': request.form['email']}))
    else:
    	return redirect('account')

@app.route('/processData', methods=['POST','GET'])
def processData():
    if request.method == 'POST':

        
        
        data = dict(request.form)
        anno = {}
        csv_data = [['filename','width','height','class','xmin','ymin','xmax','ymax']]
        row = []

        print('List start')

        for x in range(0, int(len(data)/10)):
            cell_list = []
            cell_list.append(data['data['+str(x)+'][target][source]'].split('/')[-1]) #filename
            cell_list.append(resolution('./static/upload/' + data['data['+str(x)+'][target][source]'].split('/')[-1])[1]) #width
            cell_list.append(resolution('./static/upload/' + data['data['+str(x)+'][target][source]'].split('/')[-1])[0]) #height
            cell_list.append(data['data['+str(x)+'][body][0][value]']) #class
            cell_list.append(data['data['+str(x)+'][target][selector][value]'].split(':')[-1].split(',')[0]) #xmin
            cell_list.append(data['data['+str(x)+'][target][selector][value]'].split(':')[-1].split(',')[1]) #ymin
            cell_list.append(data['data['+str(x)+'][target][selector][value]'].split(':')[-1].split(',')[2]) #xmax
            cell_list.append(data['data['+str(x)+'][target][selector][value]'].split(':')[-1].split(',')[3]) #ymax

            csv_data.append(cell_list)
    
        email = session['user']     
        with open('./static/user/'+email+'.csv', 'w+', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(csv_data)



@app.route('/logout')
def logout():
	session.pop('user', None)
	return redirect(url_for('main'))

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/contact')
def contact():
	return render_template('contact.html')

if __name__ == "__main__":
    app.run(debug=True)