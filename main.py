import os
import sqlite3
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from config import settings
from data import SQLRepository
from model import GarchModel
from starlette.responses import HTMLResponse

class FitIn(BaseModel):
    ticker: str
    use_new_data: bool
    n_observations: int
    p: int
    q: int

class FitOut(FitIn):
    success: bool
    message: str

class PredictIn(BaseModel):
    ticker: str
    n_minutes: int

class PredictOut(PredictIn):
    success: bool
    forecast: dict
    message: str

def build_model(ticker, use_new_data):
    connection = sqlite3.connect(settings.db_name, check_same_thread=False)
    repo = SQLRepository(connection=connection)
    model = GarchModel(ticker=ticker, use_new_data=use_new_data, repo=repo)
    return model

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"))
html_file_path = os.path.join(os.path.dirname(__file__), "docs", "index.html")

@app.get("/", response_class=HTMLResponse)
async def get_volatility_forecasts():
    try:
        with open(html_file_path, "r") as html_file:
            html_content = html_file.read()

        return HTMLResponse(
            content=html_content, status_code=200, headers={"Content-Type": "text/html"}
        )

    except FileNotFoundError:
        return HTMLResponse(
            content=f"Error: HTML file not found",
            status_code=404,
            headers={"Content-Type": "text/html"},
        )
    except Exception as e:
        return HTMLResponse(
            content=f"Error: {str(e)}",
            status_code=500,
            headers={"Content-Type": "text/html"},
        )

@app.post("/fit", status_code=200, response_model=FitOut)
def fit_model(request: FitIn):
    response = request.dict()
    try:
        model = build_model(ticker=request.ticker, use_new_data=request.use_new_data)
        model.wrangle_data(n_observations=request.n_observations)
        model.fit(p=request.p, q=request.q)
        filename = model.dump()
        response["success"] = True
        response[
            "message"
        ] = f"Trained and saved {filename}. Metrics: AIC {model.aic}, BIC {model.bic}."
    except FileNotFoundError:
        response["success"] = False
        response["message"] = "Error: Data file not found."
    except Exception as e:
        response["success"] = False
        response["message"] = str(e)
    return response

@app.post("/predict", status_code=200, response_model=PredictOut)
def get_prediction(request: PredictIn):
    response = request.dict()
    try:
        model = build_model(ticker=request.ticker, use_new_data=False)
        model.load()
        prediction = model.predict_volatility(horizon=request.n_minutes)
        response["success"] = True
        response["forecast"] = prediction
        response["message"] = ""
    except FileNotFoundError:
        response["success"] = False
        response["forecast"] = {}
        response["message"] = "Error: Model file not found."
    except Exception as e:
        response["success"] = False
        response["forecast"] = {}
        response["message"] = str(e)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
