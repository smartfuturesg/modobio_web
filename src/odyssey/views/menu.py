# Recursive navigation menu generation
# 
# A menu is a tuple () of dicts {}.
# Each menu item dict has the keywords 'title' and either 'url' or 'submenu'.
# The value for 'submenu' is another menu with the same structure.

menu = (
    {'title': 'Intake', 'submenu': (
        {'title': 'Client info', 'url': 'intake.clientinfo'},
        {'title': 'Forms', 'submenu': (
            {'title': 'Consent form', 'url': 'intake.consent'},
            {'title': 'Release form', 'url': 'intake.release'},
            {'title': 'Financial form', 'url': 'intake.financial'},
            {'title': 'Send forms', 'url': 'intake.send'})},
        {'title': 'Contracts', 'submenu': (
            {'title': 'Initial consult', 'url': 'intake.consult'},
            {'title': 'Subscription', 'url': 'intake.subscription'})}
    )},
    {'title': 'Doctor', 'submenu': (
        {'title': 'Medical history', 'url': 'doctor.history'},
        # {'title': 'Consult', 'url': ''}
    )},
    {'title': 'Physical therapist', 'submenu': (
        {'title': 'Therapy history', 'url': 'pt.history'},
        {'title': 'Mobility assessment', 'url': 'pt.mobility'},
        # {'title': 'Consult', 'url': ''}
    )},
    {'title': 'Trainer', 'submenu': ()}
)
