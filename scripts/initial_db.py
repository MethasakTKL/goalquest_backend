import sys
from pathlib import Path

projectroot = Path(__file__).parent.parent
sys.path.insert(0, str(projectroot))

from goalquest_backend import config, models

import asyncio

if __name__ == "__main__":
    settings = config.get_settings()
    models.init_db(settings)
    asyncio.run(models.recreate_table())