import requests
import platform
try:
    from qgis.core import Qgis
except ImportError:
    # for QGIS version < 3.x
    from qgis.core import QGis as Qgis

# There's no easy way to distribute a QGIS plugin with extra dependencies, and
# one way is to make sure that pip is installed and then install the required deps.
# see: https://gis.stackexchange.com/questions/196002/development-of-a-plugin-which-depends-on-an-external-python-library
try:
    import pip
except:
    r = requests.get('https://bootstrap.pypa.io/get-pip.py',
                     allow_redirects=False)
    exec(r.content)
    import pip
    # just in case the included version is old
    pip.main(['install', '--upgrade', 'pip'])
try:
    import sentry_sdk
except:
    pip.main(['install', 'sentry-sdk==1.24.0'])
    import sentry_sdk

PLUGIN_VERSION='1.0.5'
PLUGIN_ENVIRONMENT='local'

def init_sentry():
    sentry_sdk.init(
        dsn="https://2d2c8d43150e46c6a73bde4f5a039715@o305787.ingest.sentry.io/4505239708172288",
        traces_sample_rate=0.1,
    )

    sentry_sdk.set_tag('environment', PLUGIN_ENVIRONMENT)
    sentry_sdk.set_tag('version', PLUGIN_VERSION)
    sentry_sdk.set_tag('platform.platform', platform.platform())
    sentry_sdk.set_tag('platform.system', platform.system())
    sentry_sdk.set_tag('qgis.version', Qgis.QGIS_VERSION)
