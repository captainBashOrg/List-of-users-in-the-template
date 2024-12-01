# python -m uvicorn main:app --reload
import uvicorn
from fastapi import FastAPI, Path, status, Body, HTTPException, Request, Form

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Annotated, List


app = FastAPI()


users: List['User'] = []

templates = Jinja2Templates(directory="templates")


class User(BaseModel):
    id: int
    username: str
    age: int


@app.get('/', response_class=HTMLResponse)
async def get_users(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("users.html", {"request": request, "users": users})


@app.get('/user/{user_id}', response_class=HTMLResponse)
async def get_user(request: Request, user_id: int) -> HTMLResponse:
    user = next((user for user in users if user.id == user_id), None)
    if user:
        return templates.TemplateResponse("users.html", {"request": request, "user": user})
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.post("/user/{username}/{age}")
async def create_user(username: Annotated[str, Path(min_length=5,
                                                    max_length=30,
                                                    description="Enter username",
                                                    example_="UrbanUser")],
                      age: Annotated[int, Path(ge=18,
                                               le=120,
                                               description="Enter age",
                                               example_="24")]) -> User:
    current_id = users[-1].id + 1 if users else 1
    current_user = User(id=current_id, username=username, age=age)
    users.append(current_user)
    return current_user


@app.put("/user/{user_id}/{username}/{age}")
async def update_user(user_id: Annotated[int, Path(ge=1,
                                                   le=1000000,
                                                   description="Enter user_id",
                                                   example_="24")],
                      username: Annotated[str, Path(min_length=5,
                                                    max_length=30,
                                                    description="Enter username",
                                                    example_="UrbanUser")],
                      age: Annotated[int, Path(ge=18,
                                               le=120,
                                               description="Enter age",
                                               example_="24")]) -> User:
    for user in users:
        if user.id == user_id:
            user.username = username
            user.age = age
            return user
    raise HTTPException(status_code=404, detail="The User was not found")


@app.delete("/user/{user_id}")
async def delete_user(user_id: Annotated[int, Path(ge=1,
                                                   le=1000000,
                                                   description="Enter user_id",
                                                   example_="24")]) -> User:
    for i, user in enumerate(users):
        if user.id == user_id:
            deleted_user = users.pop(i)
            return deleted_user
    raise HTTPException(status_code=404, detail="The User was not found")


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level='info')

