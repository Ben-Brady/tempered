from flask import Flask, render_template
from tempered import Tempered, components

app = Flask(__name__, template_folder="real_world/jinja")


@app.get("/")
def page():
    return render_template("")


if __name__ == "__main__":
    Tempered("real_world/tempered").build_static()
    app.run()
