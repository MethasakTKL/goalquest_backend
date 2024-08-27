from . import users,rewards,points


def init_router(app):    
    app.include_router(users.router)
    app.include_router(points.router)
    app.include_router(rewards.router)
