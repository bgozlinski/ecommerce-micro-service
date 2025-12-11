from fastapi import FastAPI


app = FastAPI()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "product-service"}

@app.get("/")
async def root():
    return {"message": "Product Service API", "version": "0.1.0"}
