from . import users,rewards


def init_router(app):    
    app.include_router(users.router)
    app.include_router(rewards.router)
