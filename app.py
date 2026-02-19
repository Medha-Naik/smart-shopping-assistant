from flask import Flask,render_template, jsonify,request
from flask_cors import CORS
from flipkart_scraper import scrape_flipkart

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

@app.route("/results.html")
def results():
    return render_template('results.html')

@app.route("/scraper")
def products():
    query= request.args.get('q')

    if not query:
        return jsonify({'error':'Please provide search query'})
    
    data=scrape_flipkart(query)

    if not data:
        return jsonify({'error':'NO products found'})
    
    return jsonify(data)



if __name__ == "__main__":
    app.run(debug=True)

