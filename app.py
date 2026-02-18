from flask import Flask,render_template, jsonify,request
from flask_cors import CORS

app= Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/search")
def search_product():
    query=request.args.get('q')
    results=[
        {
            "name":"iphone 15 128GB",
            "image":"https://via.placeholder.com/200",
            "prices": [
                {"site": "Amazon", "price": 79999, "url": "#"},
                {"site": "Flipkart", "price": 78499, "url": "#"}
            ]
        }
    ]
    return jsonify(results)

@app.route("/results")
def results():
    return render_template('results.html')

if __name__ == "__main__":
    app.run(debug=True)

