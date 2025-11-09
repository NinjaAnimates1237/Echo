from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

users = {}
friends = {}
messages = {}
servers = {}
notifications = {}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    if username in users:
        return RedirectResponse("/", status_code=303)
    users[username] = {"password": password}
    friends[username] = []
    messages[username] = []
    servers[username] = []
    notifications[username] = []
    return RedirectResponse("/", status_code=303)

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username not in users or users[username]["password"] != password:
        return RedirectResponse("/", status_code=303)
    return RedirectResponse(f"/chat?user={username}", status_code=303)

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request, user: str):
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "user": user,
        "friends": friends.get(user, []),
        "messages": messages.get(user, []),
        "notifications": notifications.get(user, []),
        "servers": servers.get(user, [])
    })

@app.post("/add_friend")
async def add_friend(username: str = Form(...), friend: str = Form(...)):
    if friend in users and friend not in friends[username]:
        friends[username].append(friend)
        friends[friend].append(username)
        notifications[friend].append(f"👋 {username} added you as a friend!")
    return RedirectResponse(f"/chat?user={username}", status_code=303)

@app.post("/send_message")
async def send_message(sender: str = Form(...), receiver: str = Form(...), content: str = Form(...)):
    if receiver in users:
        messages[receiver].append({"from": sender, "content": content})
        notifications[receiver].append(f"💬 Message from {sender}: {content}")
    return RedirectResponse(f"/chat?user={sender}", status_code=303)

@app.post("/create_server")
async def create_server(user: str = Form(...), server_name: str = Form(...)):
    servers[user].append(server_name)
    notifications[user].append(f"🌐 Server '{server_name}' created!")
    return RedirectResponse(f"/chat?user={user}", status_code=303)

@app.post("/post_server_thread")
async def post_server_thread(user: str = Form(...), server_name: str = Form(...), content: str = Form(...)):
    notifications[user].append(f"🧵 New thread in '{server_name}': {content}")
    return RedirectResponse(f"/chat?user={user}", status_code=303)
