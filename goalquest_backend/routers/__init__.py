from . import redeems, users,rewards,points,goals,tasks,done_tasks


def init_router(app):    
    app.include_router(users.router)
    app.include_router(points.router)
    app.include_router(goals.router)
    app.include_router(tasks.router)
<<<<<<< HEAD
    app.include_router(done_tasks.router)
=======

    app.include_router(rewards.router)
    app.include_router(redeems.router)
>>>>>>> 73166a998d08edbb244570c861981c628393d8c2
