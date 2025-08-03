from flask import Blueprint, request, jsonify, render_template, redirect, url_for
import requests

main = Blueprint('main', __name__)

@main.route('/hello', methods=['GET'])
def hello():
    return "Hello, Fong!"

# @main.route('/submit', methods=['POST'])
# def submit():
#     data = request.get_json()
#     name = data.get('name')
#     course = data.get("course")
#     return "Welcome to " + course + " , " + name + "!"

# @main.route('/sum', methods=['POST'])
# def sum_numbers():
    data = request.get_json()
    a = data.get("a")
    b = data.get("b")
    return jsonify({"sum": a + b})

# @main.route('/characters', methods=['GET'])
# def characters():
#     url = "https://hp-api.onrender.com/api/characters"
#     response = requests.get(url)
#     data = response.json()
#     return render_template('characters.html', characters=data[:10])

books = []

@main.route("/")
def index():
    return render_template("books.html", books=books)

@main.route("/add", methods=["POST"])
def add_book():
    formData = request.form
    
    id = formData["id"]
    quantity = int(formData["quantity"])
    name = formData["name"]
    
    new_book = {
        "id": id,
        "name": name,
        "quantity": quantity,
    }
    
    books.append(new_book)
    
    
    return redirect(url_for("main.index"))