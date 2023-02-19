import os

bind = '0.0.0.0:' + str(os.getenv('PORT', 9876))

# Debugging
reload = True

# Logging
accesslog = '-'
loglevel = 'info'
#loglevel = 'debug'
logfile = './log/app.log'
logconfig = None

# Proc Name
proc_name = 'Infrastructure-Practice-Flask'

# Worker Processes
workers = 2
worker_class = 'sync'
