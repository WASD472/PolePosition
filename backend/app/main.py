from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app import models
from app.routers import circuits, drivers, constructors, grandprix, racesessions, results, standings,qualifying


Base.metadata.create_all(bind=engine)

app = FastAPI(title="PolePosition API")



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(circuits.router)
app.include_router(drivers.router)
app.include_router(constructors.router)
app.include_router(grandprix.router)
app.include_router(racesessions.router)
app.include_router(results.router)
app.include_router(standings.router)
app.include_router(qualifying.router)







@app.get("/")
def root():
    return {"message": "PolePosition API работает"}