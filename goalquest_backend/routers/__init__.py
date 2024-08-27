from . import users

def init_router(app):    
    app.include_router(users.router)
