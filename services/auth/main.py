from fastapi import FastAPI

app = FastAPI()

@app.get("/healthchecker")
def healthchecker():
    return {"status": "ok"}