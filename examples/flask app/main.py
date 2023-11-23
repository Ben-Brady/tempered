from tempered import Tempered
from datetime import datetime
import bs4
import components
try:
    from flask import Flask
except:
    print("You need flask installed for this example")
    exit()


app = Flask(__name__)
tempered = Tempered("./templates")
tempered.build_to(components)

@app.get("/")
def index():
    return components.Index()

@app.get("/about")
def about():
    return components.About()


@app.get("/contact")
def contact():
    return components.Contact()


if __name__ == "__main__":
    app.run(
        debug=True,
        extra_files=tempered.template_files,
    )
