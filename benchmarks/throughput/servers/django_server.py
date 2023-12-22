from flask import Flask
from tempered import Tempered, components

app = Flask(__name__)


@app.get("/")
def page():
    return components.page()


if __name__ == "__main__":
    Tempered("real_world/tempered").build_static()
    app.run()
