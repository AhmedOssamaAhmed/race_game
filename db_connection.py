from flask import Flask, request, url_for,jsonify
from flask_mysqldb import MySQL
from threading import Thread
import zmq

app = Flask(__name__)

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'gfIIb100%s'
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
        return "incorrect password"
    else:
        return "login success"

def notify_trackers(game_id, trackers):
    context = zmq.Context()
    s = context.socket(zmq.PUSH)
    s.connect("tcp://%s:8787" % tracker[0])
    s.send_string("%s %s SG %s" % (game_id, 0, tracker[1]))
    s.close()

    s2 = context.socket(zmq.PUSH)
    s2.connect("tcp://%s:8787" % tracker[1])
    s2.send_string("%s %s SG %s" % (game_id, 0, tracker[0]))
    s2.close()

tracker = ["178.79.133.165", "109.74.206.118"]
@app.route('/create_game' , methods=["POST"])
def create_game():
    cur = mysql.connection.cursor()
    game_name = request.form['game_name']
    num_players = request.form['num_players']

    cur.execute(f"INSERT INTO game (game_name,num_players, tracker_1_ip,tracker_2_ip, done) VALUES ('{game_name}',{num_players},'{tracker[0]}','{tracker[1]}', 0)")
    # Commit the changes to the database
    mysql.connection.commit()

    game_id = cur.lastrowid 
    # Close the cursor
    cur.close()
    print(game_id)

    Thread(target=notify_trackers, args=(game_id, tracker)).start()

    return jsonify([game_id, tracker])

@app.route('/list_games' , methods=["GET"])
def list_games():
    cur = mysql.connection.cursor()
    query = f"SELECT * FROM game WHERE done = 0"
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

@app.route('/list_tracker_games', methods=["POST"])
def list_tracker_games():
    cur = mysql.connection.cursor()
    ip = request.form['ip']
    query = f"SELECT * FROM game WHERE (tracker_1_ip = '{ip}' OR tracker_2_ip = '{ip}') AND done = 0"
    cur.execute(query)
    records = cur.fetchall()
    json_response = []
    for record in records:
        temp = []
        for value in record:
            temp.append(value)
        json_response.append(temp)
    cur.close()
    return jsonify(json_response)

@app.route('/done', methods=["POST"]):
def done():
    cur = mysql.connection.cursor()
    game_id = request.form['game_id']
    query = f"UPDATE game SET done = 1 WHERE id = {game_id};"
    cur.execute(query)
    return "OK" 


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

