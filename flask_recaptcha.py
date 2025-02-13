"""
The new Google ReCaptcha implementation for Flask without Flask-WTF
Can be used as standalone
"""

__NAME__ = "Flask-ReCaptcha"
__version__ = "0.5.0"
__license__ = "MIT"
__author__ = "Mardix"
__copyright__ = "(c) 2015 Mardix"

try:
    from flask import request
    try:
        from jinja2 import Markup
    except ImportError:
        from markupsafe import Markup
    import requests
except ImportError as ex:
    print("Missing dependencies")


class DEFAULTS(object):
    IS_ENABLED = True
    THEME = "light"
    TYPE = "image"
    SIZE = "normal"
    LANGUAGE = "en"
    TABINDEX = 0
    SCRIPT_ARGS = ""


class ReCaptcha(object):

    VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
    site_key = None
    secret_key = None
    is_enabled = False

    def __init__(self, app=None, site_key=None, secret_key=None, is_enabled=True, **kwargs):
        if site_key:
            self.site_key = site_key
            self.secret_key = secret_key
            self.is_enabled = is_enabled
            self.theme = kwargs.get('theme', DEFAULTS.THEME)
            self.type = kwargs.get('type', DEFAULTS.TYPE)
            self.size = kwargs.get('size', DEFAULTS.SIZE)
            self.language = kwargs.get('language', DEFAULTS.LANGUAGE)
            self.tabindex = kwargs.get('tabindex', DEFAULTS.TABINDEX)
            self.script_args = kwargs.get('script_args', DEFAULTS.TABINDEX)

        elif app:
            self.init_app(app=app)

    def init_app(self, app=None):
        self.__init__(site_key=app.config.get("RECAPTCHA_SITE_KEY"),
                      secret_key=app.config.get("RECAPTCHA_SECRET_KEY"),
                      is_enabled=app.config.get("RECAPTCHA_ENABLED", DEFAULTS.IS_ENABLED),
                      theme=app.config.get("RECAPTCHA_THEME", DEFAULTS.THEME),
                      type=app.config.get("RECAPTCHA_TYPE", DEFAULTS.TYPE),
                      size=app.config.get("RECAPTCHA_SIZE", DEFAULTS.SIZE),
                      language=app.config.get("RECAPTCHA_LANGUAGE", DEFAULTS.LANGUAGE),
                      tabindex=app.config.get("RECAPTCHA_TABINDEX", DEFAULTS.TABINDEX),
                      script_args=app.config.get("RECAPTCHA_SCRIPT_ARGS", DEFAULTS.SCRIPT_ARGS))

        @app.context_processor
        def get_code():
            return dict(recaptcha=Markup(self.get_code()))

    def get_code(self):
        """
        Returns the new ReCaptcha code
        :return:
        """
        return "" if not self.is_enabled else ("""

        <script src='//www.google.com/recaptcha/api.js?{SCRIPT_ARGS}'></script>
        <div class="g-recaptcha" data-sitekey="{SITE_KEY}" data-theme="{THEME}" data-type="{TYPE}" data-size="{SIZE}"\
         data-tabindex="{TABINDEX}"></div>
        """.format(SCRIPT_ARGS=self.script_args, SITE_KEY=self.site_key, THEME=self.theme, TYPE=self.type, SIZE=self.size, LANGUAGE=self.language, TABINDEX=self.tabindex))

    def verify(self, response=None, remote_ip=None):
        if self.is_enabled:
            data = {
                "secret": self.secret_key,
                "response": response or request.form.get('g-recaptcha-response'),
                "remoteip": remote_ip or request.environ.get('REMOTE_ADDR')
            }

            r = requests.get(self.VERIFY_URL, params=data)
            return r.json()["success"] if r.status_code == 200 else False
        return True
