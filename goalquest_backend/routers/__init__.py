from . import root
from . import redeems
from . import users
from . import rewards
from . import points
from . import goals
from . import tasks
from . import action_tasks
from . import authentication
from . import earn_history


def init_router(app):    
    app.include_router(root.router)
    app.include_router(authentication.router)



    app.include_router(users.router)
    app.include_router(points.router)

    app.include_router(goals.router)
    app.include_router(tasks.router)

    app.include_router(action_tasks.router)

    app.include_router(rewards.router)
    app.include_router(redeems.router)
    app.include_router(earn_history.router)
