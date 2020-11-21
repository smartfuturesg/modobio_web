"""
The views connect the :mod:`odyssey.models` to the webpages rendered from templates using the forms in :mod:`odyssey.forms`. The views generate :meth:`flask.Flask.route` (URLs) to the rendered pages.
"""

import odyssey.views.main
import odyssey.views.intake
import odyssey.views.doctor
import odyssey.views.pt
