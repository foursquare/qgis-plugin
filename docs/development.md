Plugin development
==================

## Setup

Instructions are aimed at developers using MacOS, but similar steps should work on different platforms as well.

Instructions were confirmed to be working well with a combination of: Python 3.9.5, QGIS 3.30+, and PyQT 5.

1. Install QGIS app from https://qgis.org/en/site/forusers/download.html
2. We rely on [qgis_plugin_tools](https://github.com/GispoCoding/qgis_plugin_tools), so when cloning the repo, make sure to clone it recursively, with submodules:

```bash
git clone --recurse-submodules https://github.com/UnfoldedInc/qgis-plugin.git
```

3. Set up tools:

```bash
python3 --version # make sure that you're using Python 3.9.5
pip3 install --upgrade pip # upgrade pip to latest
pip3 install --upgrade setuptools # upgrade setuptools to latest
```

4. Install Qt and PyQT:

```bash
brew install qt@5 # our plugin relies on v5, so we make sure it's that version
export PATH="/opt/homebrew/opt/qt5/bin:$PATH" # makes sure that qmake is in your PATH
pip3 install pyqt5-sip
pip3 install pyqt5 --config-settings --confirm-license= --verbose # in some cases, the install script gets stuck on license step and this way we just automatically confirm it
```

5. Install dependencies:

```bash
cd qgis-plugin
pip install -r requirements.txt

export PYTHONPATH=/Applications/Qgis.app/Contents/Resources/python # this makes sure that the version of python with bundled `qgis` module can be found
```

6. The build script:

If you're on Mac, you want to comment out the lines #70 and #71 in `qgis-plugin/Unfolded/qgis_plugin_tools/infrastructure/plugin_maker.py`. This is because Apple returns `"darwin"` as a OS identifier, so this OS check mistakenly thinks it's a Windows machine, and instead, we just let it fall through to the actual case for Mac.

Now you can run the build script and deploy it to the QGIS' plugins folder:

```bash
cd qgis-plugin/Unfolded
python3 build.py deploy
```

This should be the end of your setup and if you manage to run `build.py` script without any errors, that's a confirmation that everything is set up correctly.

## Development workflow

- make changes to the plugin inside `/Unfolded` folder
- run `python3 build.py deploy`, this packages the plugin and copies it to the QGIS' plugins folder (usually `/Users/<username>/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins`; or see [plugin's dir location](https://gis.stackexchange.com/questions/274311/qgis-3-plugin-folder-location))
  - this does not publish the plugin to the official plugin registry, just installs it locally! (for releasing it to the remote registry, see [Creating a release](#creating-a-release) section)
  - additionally, you can set up a filesystem watcher to monitor entire folder and automatically execute the deploy command so you don't have to do it manually every time
- to use the freshly "deployed" plugin inside QGIS you can, either:
  - restart QGIS app, and it will reload all plugins; or
  - go to "Installed Plugins" and deselect and then again select your plugin in the list, effectively reloading it; or
  - use [plugin-reloader](https://plugins.qgis.org/plugins/plugin_reloader/) plugin (← this has the best DX and is recommended)

For debugging use:
- dev log (via <kbd>View</kbd> → <kbd>Panels</kbd> → <kbd>Log Messages</kbd>)
  - this gives you multiple output windows for all the different plugins and internal QGIS python interpreter, and is basically the main debugging tool you'll be using
- REPL Python console (via <kbd>Plugins</kbd> → <kbd>Python Console</kbd>)
  - `qgis` module is available to all the plugins, and is automatically bound to them when executing plugins and is not available as a general dependency that you can freely import and use in normal Python scripts, so this is the only way you have access to it in any Python environment other than within QGIS plugin runtime

## Adding or editing  source files
If you create or edit source files make sure that:

* they contain relative imports
    ```python

    from ..utils.exceptions import TestException # Good

    from Unfolded.utils.exceptions import TestException # Bad
    ```
* they will be found by [build.py](../Unfolded/build.py) script (`py_files` and `ui_files` values)
* you consider adding test files for the new functionality

## QGIS documentation and help

- QGIS docs: https://docs.qgis.org/3.28/en/docs/user_manual/
  - make sure you're viewing the docs of the right SDK version
- GIS stachexchange is your friend: https://gis.stackexchange.com/
- when googling, adding "PyQGIS" keyword helps narrow down search results quite a lot

## Testing
Install Docker, docker-compose and python packages listed in [requirements.txt](../requirements.txt)
to run tests with:

```shell script
python build.py test
```
## Translating

#### Translating with transifex

Fill in `transifex_coordinator` (Transifex username) and `transifex_organization`
in [.qgis-plugin-ci](../.qgis-plugin-ci) to use Transifex translation.


##### Pushing / creating new translations

* First install [Transifex CLI](https://docs.transifex.com/client/installing-the-client) and
  [qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci)
* Make sure command `pylupdate5` works. Otherwise install it with `pip install pyqt5`
* Run `qgis-plugin-ci push-translation <your-transifex-token>`
* Go to your Transifex site, add some languages and start translating
* Copy [push_translations.yml](push_translations.yml) file to [workflows](../.github/workflows) folder to enable
  automatic pushing after commits to master
* Add this badge ![](https://github.com/UnfoldedInc/qgis-plugin/workflows/Translations/badge.svg) to
  the [README](../README.md)

##### Pulling
There is no need to pull if you configure `--transifex-token` into your
[release](../.github/workflows/release.yml) workflow (remember to use Github Secrets).
Remember to uncomment the lrelease section as well.
You can however pull manually to test the process.
* Run `qgis-plugin-ci pull-translation --compile <your-transifex-token>`

#### Translating with QT Linguistic (if Transifex not available)

The translation files are in [i18n](../Unfolded/resources/i18n) folder. Translatable content in python files is code
such as `tr(u"Hello World")`.

To update language *.ts* files to contain newest lines to translate, run
```shell script
python build.py transup
```

You can then open the *.ts* files you wish to translate with Qt Linguist and make the changes.

Compile the translations to *.qm* files with:
```shell script
python build.py transcompile
```


## Creating a release
Follow these steps to create a release
* Add changelog information to [CHANGELOG.md](../CHANGELOG.md) using this
[format](https://raw.githubusercontent.com/opengisch/qgis-plugin-ci/master/CHANGELOG.md)
* Update `PLUGIN_VERSION` variable in `sentry.py`
* Make a new commit. (`git add -A && git commit -m "Release v0.1.0"`)
* Create new tag for it (`git tag -a v0.1.0 -m "Version v0.1.0"`)
* Push tag to Github using `git push --follow-tags`
* Create Github release
* [qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci) adds release zip automatically as an asset
