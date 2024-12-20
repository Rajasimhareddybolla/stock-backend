from flask import Flask, request, jsonify
from flask_cors import CORS
import cs50

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
db = cs50.SQL("sqlite:///stock.db")

# Create required tables if they don't exist
db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        mail TEXT NOT NULL UNIQUE,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
""")

db.execute("""
    CREATE TABLE IF NOT EXISTS stock (
        stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
        id INTEGER NOT NULL,
        stock TEXT NOT NULL,
        FOREIGN KEY (id) REFERENCES users(id)
    )
""")

# Create stocks table
db.execute("""
    CREATE TABLE IF NOT EXISTS stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        change REAL NOT NULL,
        volume INTEGER NOT NULL,
        market_cap TEXT NOT NULL,
        sector TEXT NOT NULL
    )
""")

# Initialize stocks if table is empty
def init_stocks():
    stocks = db.execute("SELECT COUNT(*) as count FROM stocks")[0]['count']
    if stocks == 0:
        initial_stocks = [
            ("RELIANCE", "Reliance Industries", 2500.25, 2.5, 1000000, "16.75T", "Energy"),
            ("TCS", "Tata Consultancy Services", 3450.80, -1.2, 500000, "12.65T", "IT"),
            ("HDFCBANK", "HDFC Bank", 1605.15, 0.8, 750000, "8.92T", "Finance"),
            ("INFY", "Infosys", 1380.50, -0.5, 600000, "5.78T", "IT"),
            ("HINDUNILVR", "Hindustan Unilever", 2325.75, 1.7, 300000, "5.46T", "FMCG"),
            ("ICICIBANK", "ICICI Bank", 945.60, 1.2, 820000, "6.58T", "Finance"),
            ("ITC", "ITC Limited", 415.30, -0.3, 1200000, "5.15T", "FMCG"),
            ("SBIN", "State Bank of India", 565.90, 2.1, 950000, "5.05T", "Finance"),
            ("BHARTIARTL", "Bharti Airtel", 875.45, 0.9, 480000, "4.87T", "Telecom"),
            ("BAJFINANCE", "Bajaj Finance", 6890.20, -1.8, 220000, "4.16T", "Finance")
        ]
        
        for stock in initial_stocks:
            db.execute("""
                INSERT INTO stocks (symbol, name, price, change, volume, market_cap, sector)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, *stock)

# Initialize stocks when app starts
init_stocks()

@app.route("/register" , methods = ["POST"])
def register():
    if request.method == "POST":
        data = request.json
        mail= data["mail"]
        username = data["username"]
        password= data["password"]
        c_password = data["confirm_password"]
        if password == c_password:
            users  = db.execute("select * from users")
            id = 0 
            for user in users:
                id +=1
                if user["mail"] == mail or user["username"] == username:
                    return jsonify({"message" : "username or mail already exists"})
            db.execute("INSERT INTO users (id ,mail , username , password) VALUES (?,?,?,?)", id , mail , username , password)
            return jsonify({"message" : "user created successfully" , "id":id})
        else:
            return jsonify({"message": "Passwords do not match"}), 400
    return jsonify({"message":"mehtod not allowed"})    

@app.route("/login" , methods = ["POST"])
def login():
    if request.method == "POST":
        data = request.json
        mail = data["mail"]
        password = data["password"]
        users = db.execute("SELECT * FROM users WHERE mail = ? AND password = ?", mail ,password)
        id  = users[0]["id"]
        return jsonify({"message" : "logged in successfully" , "id":id})
    else:
        return jsonify({"message":"method not allowed"})
    

@app.route("/save_stock" , methods = ["POST"])
def save_stock():
    if request.method == "POST":
        data = request.json
        id = data["id"]
        stock = data["stock"]
        db.execute("INSERT INTO stock (id , stock) VALUES (?,?)", id , stock)
        return jsonify({"message" : "stock saved successfully" , "id":id})
    else:
        return jsonify({"message":"method not allowed"})
    
@app.route("/show_stocks")
def show_stocks():
    id = request.args.get("id")
    stocks = db.execute("SELECT * FROM stock WHERE id = ?", id)
    return jsonify({"stocks":stocks})

@app.route("/api/stocks", methods=["GET"])
def get_stocks():
    stocks = db.execute("SELECT * FROM stocks")
    return jsonify({"stocks": stocks})

@app.route("/api/stocks/<symbol>", methods=["GET"])
def get_stock(symbol):
    stock = db.execute("SELECT * FROM stocks WHERE symbol = ?", symbol)
    if stock:
        return jsonify({"stock": stock[0]})
    return jsonify({"message": "Stock not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
