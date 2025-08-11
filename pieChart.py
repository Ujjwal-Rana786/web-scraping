
from  flask import Flask, render_template, url_for, redirect
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re 
import matplotlib.pyplot as plt 

app = Flask(__name__)

# flask :- flask is class 

# __name__ :-  This is a special variable in Python that holds the name of the current module. When the module is run directly, __name__ is set to '__main__'. When it is imported from another module, __name__ is set to the module's name.

# app :- is a object(instance) of a class.use this object to define routes , run the server and configure the application

app.config['UPLOAD_FOLDER'] = 'static'

# Global Dataframe to hold scraped data
scraped_data = pd.DataFrame()

@app.route('/')
def scrape_books():
    global scraped_data
    url = "http://books.toscrape.com/catalogue/category/books/science_22/index.html"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    products = []

    items = soup.find_all("article", class_="product_pod")  # corrected class name

    for item in items:
        name_tag = item.find("h3").find("a")
        price_tag = item.find("p", class_="price_color")

        name = name_tag.get("title") if name_tag else "N/A"
        price_text = price_tag.get_text(strip=True) if price_tag else "£0"
        price_clean = re.sub(r"[^\d.]", "", price_text)  # keep the decimal point
        price = float(price_clean) if price_clean else 0.0

        products.append([name, price])

    scraped_data = pd.DataFrame(products, columns=["Name", "Price (£)"])

    return render_template("scrape.html", table=scraped_data.to_html(index=False, classes="table table-striped"))


@app.route('/pie')    
def pie_chart():
    if scraped_data.empty:
        return redirect('/')
    
    plt.figure(figsize=(10,6))
    plt.pie(scraped_data["Price (£)"], labels=scraped_data["Name"])
    plt.title("Books prices - pie chart")
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'pie_chart.png')
    plt.savefig(chart_path)
    plt.close()
    return render_template('pie_chart.html', chart_url = url_for('static',filename='pie_chart.png'))

if __name__ == '__main__':
    app.run(debug=True ,port=3000,host="0.0.0.0")
