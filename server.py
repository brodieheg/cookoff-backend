from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
DATABASE = 'app.db'

def init_db():
    print('starting db')
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS entries (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            category TEXT NOT NULL,
                            name TEXT NOT NULL,
                            namevotes INTEGER,
                            votes INTEGER)''')
        conn.commit()

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/entries', methods=['GET'])
def get_deals():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM entries')
    entries = cursor.fetchall()
    return jsonify([dict(entry) for entry in entries])


@app.route('/init-db', methods=['GET'])
def startDb():
    init_db()
    return('started db')

@app.route('/vote', methods=['PUT'])
def confirmRing():
    conn = get_db()
    cursor = conn.cursor()
    vote = request.get_json()
    votes = []
    # use IDs to cast the votes
    meatVote = vote.get('meat')
    if (meatVote != None):
        votes.append(meatVote)
    nonMeatVote = vote.get('non-meat')
    if (nonMeatVote != None):  
        votes.append(nonMeatVote)
    sideVote = vote.get('side')
    if (sideVote != None):    
        votes.append(sideVote)
    dessertVote = vote.get('dessert')
    if (dessertVote != None):
        votes.append(dessertVote)
    nameVote = vote.get('name')
    try:
        cursor.execute('UPDATE entries SET votes = votes + 1 WHERE id IN (?, ?, ?, ?)', votes)
        cursor.execute('UPDATE entries SET namevotes = namevotes + 1 WHERE id = ?', (nameVote))
        conn.commit()
        updatedentries = cursor.fetchall()
        return jsonify([dict(entry) for entry in updatedentries]), 200
    except:
        return 400


@app.route('/delete-entries', methods=['DELETE'])
def delete_deals():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM entries')
    conn.commit()
    return jsonify({'message': 'All entries deleted'}), 201

@app.route('/entries', methods=['POST'])
def create_deal():
    data = request.get_json()

    category = data.get('category')
    name = data.get('name')
    namevotes = 0
    votes = 0

    if not category or not name :
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('''INSERT INTO deals (category, name, namevotes, votes)
                          VALUES (?, ?, ?, ?)''',
                       (category, name, namevotes, votes))
        conn.commit()
        return jsonify({'message': 'entry created successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Failed to create entry'}), 500


if __name__ == '__main__':
    init_db()
    app.run(debug=True)