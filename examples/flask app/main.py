from tempered import Tempered

try:
    from flask import Flask
except:
    print("You need flask installed for this example")
    exit()


app = Flask(__name__)
tempered = Tempered("./templates")


@app.get("/")
def index():
    return tempered.render("index.html")


@app.get("/about")
def about():
    return tempered.render("about.html")


@app.get("/contact")
def contact():
    return tempered.render("contact.html")


if __name__ == "__main__":
    app.run(
        debug=True,
        extra_files=tempered.template_files,
    )
