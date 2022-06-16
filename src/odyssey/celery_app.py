"""
The celery instance is initialized here. This is done by calling the init_celery function from 
odyssey. Doing so will ensure the correct context when working with the flask app. 

Configuration may take place in this module or from config.py. Here config variables are accessed by editing parameter in 
app.conf

Possible configuration options here: https://docs.celeryproject.org/en/stable/userguide/configuration.html#configuration

"""
import logging
logger = logging.getLogger(__name__)

from odyssey import init_celery


from odyssey.config import Config
conf = Config()

app = init_celery()

# So celery workers can discover tasks, add import paths to the modules which contain tasks
app.conf.imports = app.conf.imports + ("odyssey.tasks.periodic","odyssey.tasks.tasks")

app.conf.task_routes = {"odyssey.tasks.periodic.deploy_webhook_tasks": {'queue': 'webhook_listener'}}

app.conf.beat_max_loop_interval = 60 # max time between beat ticks
app.conf.redbeat_lock_timeout = app.conf.beat_max_loop_interval * 5
app.conf.redbeat_redis_url = conf.redbeat_redis_url

# force celery app to verify tasks
app.finalize()
