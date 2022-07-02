from lib2to3.pgen2.token import OP
from typing import Optional
from turtle import width
from fastapi import FastAPI
from pydantic import BaseModel

from calculations.base import BaseWindow

class WindowInput(BaseModel):
    height: int
    width: int
    glazing: int
    opening_direction: str
    window_type: int
    wind_value: Optional[float] = 0.
    wind_type: Optional[str] = "speed"
    opening_angle: Optional[int] = None
    max_angle: Optional[int] = 60

app = FastAPI()

@app.get("/")
def home():
    return {"Test": "Msg"}


@app.post("/api/v1/calculations/window")
async def get_window_load(input: WindowInput):

    window = BaseWindow(
        height = input.height, 
        width = input.width, 
        glazing = input.glazing, 
        opening_direction = input.opening_direction,
        window_type = input.window_type,
        wind_value = input.wind_value,
        wind_type = input.wind_type
    )

    window_load, window_load_with_wind = window.load_moment(
        opening_angle=input.opening_angle,
        max_angle=input.max_angle
    )
    
    response = {
        "window": {
            "height": window.height,
            "width": window.width,
            "surface": window.surface,
            "glazing": window.glazing,
            "sash_weight": window.sash_weight,
            "filling_weight": window.filling_weight,
            "opening_direction": window.direction,
            "window_type": window.type,
            "hinge_position": window.hinge_position
        },
        "environment": {
            "wind_speed": window.wind_speed,
            "wind_pressure": window.wind_pressure,
            "wind_load_N": window.wind_load_N
        },
        "load": {
            "progression": window_load,
            "progression_with_wind": window_load_with_wind,
            "load_moment_pull": max(window_load_with_wind.values())\
                if max(window_load_with_wind.values()) > 0 else 0,
            "load_moment_push": min(window_load_with_wind.values())\
                if min(window_load_with_wind.values()) < 0 else 0
        }
    }
    return response