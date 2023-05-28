from flask import Flask, request, url_for,jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'racegame'

mysql = MySQL(app)


@app.route('/add', methods=['POST'])
def add():
    cur = mysql.connection.cursor()

    user_name = request.form['user_name']

    cur.execute(f"INSERT INTO user (user_name) VALUES ('{user_name}')")
    # Commit the changes to the database
    mysql.connection.commit()

    # Close the cursor
    cur.close()

    return 'Record added successfully'

@app.route('/get_record_by_column_value', methods=['POST'])
def get_record_by_column_value(table_name,column_name,column_value):
    cur = mysql.connection.cursor()
    # table_name = request.form['table_name']
    # column_name = request.form['column_name']
    # column_value = request.form['column_value']
    # Construct the SQL query
    query = f"SELECT * FROM {table_name} WHERE {column_name} = '{column_value}'"

    # Execute the query with the column value as an argument
    cur.execute(query)

    # Fetch all the records
    records = cur.fetchall()
    print(records)
    json_response = []
    for record in records:
        temp = []
        for value in record:
            temp.append(value)
        json_response.append(temp)

    # Close the cursor and database connection
    cur.close()

    return json_response

@app.route('/register',methods=['POST'])
def register():
    cur = mysql.connection.cursor()
    user_name = request.form['user_name']
    password = request.form['password']

    if len(get_record_by_column_value("user","user_name",user_name)) > 0:
        return "user name already exist"
    else :
        cur.execute(f"INSERT INTO user (user_name,password) VALUES ('{user_name}','{password}')")
        # Commit the changes to the database
        mysql.connection.commit()

        # Close the cursor
        cur.close()
        return "user added"

@app.route('/login',methods=['POST'])
def login():
    cur = mysql.connection.cursor()
    user_name = request.form['user_name']
    password = request.form['password']
    user = get_record_by_column_value("user","user_name",user_name)
    if len(user) < 1 :
        return "user name not found"
    elif password != user[0][2]:
        return "false password"
    else:
        return "login success"

tracker_1_ip = ["192.168.1.1"]
tracker_2_ip = ["198.168.1.2"]
@app.route('/create_game' , methods=["POST"])
def create_game():
    cur = mysql.connection.cursor()
    game_name = request.form['game_name']

    if len(get_record_by_column_value("game", "game_name", game_name)) > 0:
        return "game name already exist"
    else:
        cur.execute(f"INSERT INTO game (game_name,tracker_1_ip,tracker_2_ip) VALUES ('{game_name}','{tracker_1_ip[0]}','{tracker_2_ip[0]}')")
        # Commit the changes to the database
        mysql.connection.commit()

        # Close the cursor
        cur.close()
        return "user added"

@app.route('/list_games' , methods=["POST"])
def list_games():
    cur = mysql.connection.cursor()
    query = f"SELECT * FROM game "
    cur.execute(query)
    records = cur.fetchall()
    print(records)
    json_response = []
    for record in records:
        temp = []
        for value in record:
            temp.append(value)
        json_response.append(temp)

    # Close the cursor and database connection
    cur.close()
    return jsonify(json_response)
if __name__ == '__main__':
    app.run()

