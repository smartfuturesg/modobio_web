from collections import OrderedDict

menu = OrderedDict(
    {'title': 'Intake', 'items': OrderedDict(
        {'title': 'Client info', 'url': 'intake.clientinfo'},
        {'title': 'Forms', 'items': OrderedDict(
            {'title': 'Consent form', 'url': 'intake.consent'},
            {'title': 'Release form', 'url': 'intake.release'},
            {'title': 'Financial form', 'url': 'intake.financial'},
            {'title': 'Send forms', 'url': 'intake.send'})},
        {'title': 'Contracts', 'items': OrderedDict(
            {'title': 'Initial consult', 'url': 'intake.consult'},
            {'title': 'Subscription', 'url': 'intake.subscription'})}
    )},
    {'title': 'Doctor', 'items': OrderedDict(
        {'title': 'Medical history', 'url': 'doctor.history'},
        {'title': 'Consult', 'url': ''}
    )},
    {'title': 'Physical therpist', 'items': OrderedDict(
        {'title': 'Therapy history', 'url': 'pt.history'},
        {'title': 'Mobility assessment', 'url': 'pt.mobility'},
        {'title': 'Consult', 'url': ''}
    )},
    {'title': 'Trainer', 'items': OrderedDict()}
)
