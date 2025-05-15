import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session


from src.routes import contact, auth, users
from src.database.db import get_db


app = FastAPI()

# origins = ["*"]
origins = ["http://localhost:8000"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contact.router, prefix="/api")
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='')


@app.get("/", tags=["main"])
def get_root():
    return {"message": "Description of all commands are availbale here: http://127.0.0.1:8000/docs"}


@app.get("/healthchecker", tags=["main"])
def healthchecker(db: Session = Depends(get_db)):
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error connecting to the database"
        )


if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, reload=True)
