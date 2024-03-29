from flask import Flask, request, jsonify, redirect, url_for,send_from_directory
from flask import render_template
import mysql.connector
import hashlib
from werkzeug.utils import secure_filename
import os
import base64

password1=input("Enter mysql database password: ")
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['DISPLAY_FOLDER'] = 'display'

from prettytable import PrettyTable

hostname = "localhost"
username = "root"
password = password1
database = "iss_project"

import os

def delete_files_in_directory(directory_path):
    try:
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted file: {filename}")
    except Exception as e:
        print(f"Error deleting files: {e}")



def get_image_format(image_data):
    # Extract the image format from the base64-encoded data
    return image_data[:image_data.find(b';')].decode('utf-8').split('/')[1]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def create_tables():
    try:
        connection = mysql.connector.connect(
            host=hostname,
            user=username,
            password=password,
            database=database
        )

        if connection.is_connected():
            cursor=connection.cursor()
            query="""CREATE TABLE  IF NOT EXISTS user_details(
                name varchar(1000),
                user_name varchar(1000) ,
                email varchar(1000) ,
                password varchar(1000) ,
                user_id INT AUTO_INCREMENT PRIMARY KEY);"""
            cursor.execute(query)
            connection.commit()
            query="""CREATE TABLE  IF NOT EXISTS  images(
            image_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT  ,
            image LONGBLOB,
            metadata varchar(1000),
            extension varchar(20)
            );"""
            cursor.execute(query)
            connection.commit()
            query="""CREATE TABLE  IF NOT EXISTS audio(
                audio_id INT AUTO_INCREMENT PRIMARY KEY,
                audio_data LONGBLOB,
                audio_metadata varchar(1000)
            );"""
            cursor.execute(query)
            connection.commit()
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection closed")

def insert_data(name1,username1, email1, password1):
    try:
        connection = mysql.connector.connect(
            host=hostname,
            user=username,
            password=password,
            database=database
        )

        if connection.is_connected():
            cursor = connection.cursor()
            query = "INSERT INTO user_details (name,user_name, email, password) VALUES (%s,%s, %s, %s)"
            data = (name1,username1, email1, password1)
            cursor.execute(query, data)
            connection.commit()

            print("Data inserted successfully!")
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection closed")

def print_table_from_mysql():
    try:
        connection = mysql.connector.connect(
            host=hostname,
            user=username,
            password=password,
            database=database
        )


        if connection.is_connected():
            print("Connected to MySQL database")

           
            cursor = connection.cursor()

            
            query = "SELECT * FROM user_details"
            cursor.execute(query)

            
            rows = cursor.fetchall()

           
            if rows:
                columns = [column[0] for column in cursor.description]
                table = PrettyTable(columns)
                table.align = 'l' 

                for row in rows:
                    table.add_row(row)

                print(table)
            else:
                print("No data found in the table.")

    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")

    finally:
        
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection closed")

def search_for_user(username_user,password_user):
    try:
        connection = mysql.connector.connect(
            host=hostname,
            user=username,
            password=password,
            database=database
        )
        if connection.is_connected():
            cursor=connection.cursor(buffered=True)
            query="SELECT * FROM user_details WHERE user_name=%s AND password=%s"
            data=(username_user,password_user)
            cursor.execute(query,data)
            connection.commit()
            row=cursor.fetchone()
            if row:
                connection.close()
                print("MySQL connection closed")
                return row[4]
            
            else:
                connection.close()
                print("MySQL connection closed")
                return 0
    
    except mysql.connector.Error as e:
            print(f"Error: {e}")
            return 0
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("MySQL connection closed")
            return 0
    return 0

def save_to_database(file_path, a,extension):
    try:
        connection = mysql.connector.connect(
            host=hostname,
            user=username,
            password=password,
            database=database
        )

        if connection.is_connected():
            cursor = connection.cursor()

            # Open the file and read the binary data
            with open(file_path, 'rb') as file:
                image_data = file.read()
               

            # Insert the data into the images table along with metadata
            query = "INSERT INTO images (image,user_id,extension) VALUES (%s, %s,%s)"
            cursor.execute(query, (image_data, a,extension))

            connection.commit()

    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

def get_images(user_id):
    try:
        connection = mysql.connector.connect(
            host=hostname,
            user=username,
            password=password,
            database=database
        )
        cursor = connection.cursor()

        # Retrieve images for the specified user_id from the database
        query = "SELECT image, extension FROM images WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        images = cursor.fetchall()

        image_data_list = []
        for image_data, image_extension in images:
            # Convert image_data to base64 for embedding in HTML
            encoded_image=base64.b64encode(image_data)

            image_data_list.append(f"data:image/{image_extension};base64,{encoded_image}")

        return image_data_list

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
@app.route('/get_all_image_ids/<int:user_id>')
def get_all_image_ids(user_id):
    try:
        connection = mysql.connector.connect(
            host=hostname,
            user=username,
            password=password,
            database=database
        )
        cursor = connection.cursor()

        # Retrieve all image IDs for the specified user_id
        query = "SELECT image_id FROM images WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        image_ids = [row[0] for row in cursor.fetchall()]

        return jsonify(image_ids)

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',target="_self")

@app.route('/login',methods=['GET','POST'])
def login():
    
    if request.method=='POST':
        username_login=request.form['username']
        password_login=request.form['password']
        hashed_password_login = hashlib.sha256(password_login.encode()).hexdigest()
        a=search_for_user(username_login,hashed_password_login)
        if a==0:
            return redirect(url_for('signup'))
        else:
            return redirect(url_for('home',user_id=a))

        
    return render_template('login.html',target="_self")

@app.route('/signup',methods=['GET','POST'])
def signup():
    
    if request.method=='POST':
        username_user=request.form['username']
        name_user=request.form['name']
        email_user=request.form['email']
        password_user=request.form['password']
        hashed_password = hashlib.sha256(password_user.encode()).hexdigest()
        insert_data(name_user, username_user, email_user, hashed_password)
        return redirect(url_for('login'))


    return render_template('signup.html',target="_self")

@app.route('/home/user/<int:user_id>',methods=['GET','POST'])
def home(user_id):
    if request.method=='POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_extension = file.filename.rsplit('.', 1)[1].lower()

            # Save the file path to the database along with metadata
            save_to_database(file_path,user_id,image_extension)
            

            return jsonify({"status": "success"})

        return jsonify({"status": "failed"})
    else:
        image_data_list = get_images(user_id)

        # Render HTML to display images
        return render_template('home.html', user_id=user_id, image_data_list=image_data_list)

            

            

@app.route('/display/<int:user_id>/<path:image_id>')
def display_image(user_id, image_id):
    # Serve the requested image from the 'display' folder
    return send_from_directory(app.config['DISPLAY_FOLDER'], image_id)


@app.route('/admin')
def admin():
    return render_template('admin.html',target="_self")

@app.route('/videopage')
def videopage():
    return render_template('videopage.html',target="_self")


if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
