""" Recursive navigation menu generation.

A menu is a tuple () of dicts {}.
Each menu item dict has the keywords 'title' and either 'url' or 'submenu'.
The value for 'submenu' is another menu with the same structure.
"""

menu = (
    {'title': 'Intake', 'submenu': (
        {'title': 'Client info', 'url': 'intake.clientinfo'},
        {'title': 'Forms', 'submenu': (
            {'title': 'Consent form', 'url': 'intake.consent'},
            {'title': 'Release form', 'url': 'intake.release'},
            {'title': 'Policies', 'url': 'intake.policies'},
            {'title': 'Send forms', 'url': 'intake.send'})},
        {'title': 'Contracts', 'submenu': (
            {'title': 'Initial consult', 'url': 'intake.consult'},
            {'title': 'Subscription', 'url': 'intake.subscription'},
            {'title': 'Individual services', 'url': 'intake.individual'})}
    )},
    {'title': 'Doctor', 'submenu': (
        {'title': 'Medical history', 'url': 'doctor.history'},
        {'title': 'Physical exam', 'url': 'doctor.physical'}
    )},
    {'title': 'Physical therapist', 'submenu': (
        {'title': 'Therapy history', 'url': 'pt.history'},
        {'title': 'Mobility assessment', 'url': 'pt.mobility'},
        # {'title': 'Consult', 'url': ''}
    )},
    {'title': 'Trainer', 'submenu': ()}
)
""" A simple, nested description of a menu.

The menu will be converted to HTML on start of the app.

:type: tuple(dict)
"""
