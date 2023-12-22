import os
print(os.environ["PYTHONPATH"])
from data import user

from fastapi import FastAPI
from tempered import Tempered
import uvicorn


app = FastAPI()
components = Tempered("real_world/tempered").build_memory()


@app.get("/")
def page():
    return components.page(user=user)


if __name__ == "__main__":
    uvicorn.run("tempered:app")
