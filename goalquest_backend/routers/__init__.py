from . import redeems, users,rewards,points,goals,tasks,done_tasks


def init_router(app):    
    app.include_router(users.router)
    app.include_router(points.router)
    app.include_router(rewards.router)
    app.include_router(redeems.router)
    app.include_router(goals.router)
    app.include_router(tasks.router)
    app.include_router(done_tasks.router)
