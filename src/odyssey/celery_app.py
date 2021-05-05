"""
The celery instance is initialized here. This is done by calling the init_celery function from 
odyssey. Doing so will ensure the correct context when working with the flask app. 

Configuration may take place in this module or from config.py. Here config variables are accessed by editing parameter in 
app.conf

Possible configuration options here: https://docs.celeryproject.org/en/stable/userguide/configuration.html#configuration

"""

from odyssey import init_celery

app = init_celery()

# So celery workers can discover tasks, add import paths to the modules which contain tasks
app.conf.imports = app.conf.imports + ("odyssey.tasks.periodic",)

# force celery app to verify tasks
app.finalize()

