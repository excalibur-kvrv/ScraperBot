# UrbanOutfittersBot
A bot to get product description, product sizes, product price from https://www.urbanoutfitters.com/

# Installation

* run `virtualenv -p python3.6 venv` to create a virtual environment
* activate the virtual environment using `source venv/bin/activate`
* run `pip install -r requirements.txt` to install all dependencies

# Usage

* run the program using `python urbanoutfittersbot.py`
* after running the program you will see a data.csv has been generated it contains the following data in the respective order

    <h2> data.csv contents:- </h2>
    <ul>
    <li>product title (string)</li>  
    <li>product description (string)</li>  
    <li>product price (string)</li>  
    <li>product colors (array)</li>
    <li>product image url (string)</li>
    <li>product sizes (array)</li>
    </ul>

# Other Requirements
* To enable the proxy feature you need to ensure that you are running tor on you local computer, to download tor browser visit https://www.torproject.org/download/, once downloaded start the browser and set proxy=True while calling bot.start()