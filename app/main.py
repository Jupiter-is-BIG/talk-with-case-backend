from fastapi import FastAPI, BackgroundTasks
from .talk import talk
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return {"message": "Talk with CASE v0.0.1"}

@app.get("/initiate", status_code=200)
async def initiate(id, actor, name, background_tasks: BackgroundTasks):
    background_tasks.add_task(talk, id, actor, name)
    return {"message" : "conversation initiated"}


@app.get("/end", status_code=200)
async def end(id):
    ACTIVE_PATH = f'/Users/clef/Desktop/bchack/app/active/{id}.txt'
    with open(ACTIVE_PATH, 'w') as file:
            file.write("0")
    return {"message" : "conversation closed"}