Plugin development
==================

## Setup

1. Install QGIS app from https://qgis.org/en/site/forusers/download.html
2. We rely on [qgis_plugin_tools](https://github.com/GispoCoding/qgis_plugin_tools), so when cloning the repo, make sure to clone it recursively, with submodules:

```bash
git clone --recurse-submodules https://github.com/foursquare/qgis-plugin.git
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

If you're on Mac, you want to comment out the lines #70 and #71 in `qgis-plugin/Foursquare/qgis_plugin_tools/infrastructure/plugin_maker.py`. This is because Apple returns `"darwin"` as a OS identifier, so this OS check mistakenly thinks it's a Windows machine, and instead, we just let it fall through to the actual case for Mac.

Now you can run the build script and deploy it to the QGIS' plugins folder:

```bash
cd qgis-plugin/Foursquare
python3 build.py deploy
```

This should be the end of your setup and if you manage to run `build.py` script without any errors, that's a confirmation that everything is set up correctly.

## Development workflow

1. make changes to the plugin inside `/Foursquare` folder
2. run `python3 build.py deploy` to package the plugin and copy it to the QGIS' plugins folder (this does not publish it, just installs it locally!)
3. restart QGIS app

And now, a new version of the plugin should be available.

## Adding or editing  source files
If you create or edit source files make sure that:

* they contain relative imports
    ```python

    from ..utils.exceptions import TestException # Good

    from Foursquare.utils.exceptions import TestException # Bad
    ```
* they will be found by [build.py](../Foursquare/build.py) script (`py_files` and `ui_files` values)
* you consider adding test files for the new functionality

## Deployment

Edit [build.py](../Foursquare/build.py) to contain working values for *profile*, *lrelease* and *pyrcc*. If you are
running on Windows, make sure the value *QGIS_INSTALLATION_DIR* points to right folder

Run the deployment with:
```shell script
python build.py deploy
```

After deploying and restarting QGIS you should see the plugin in the QGIS installed plugins
where you have to activate it.

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
* Add this badge ![](https://github.com/foursquare/qgis-plugin/workflows/Translations/badge.svg) to
  the [README](../README.md)

##### Pulling
There is no need to pull if you configure `--transifex-token` into your
[release](../.github/workflows/release.yml) workflow (remember to use Github Secrets).
Remember to uncomment the lrelease section as well.
You can however pull manually to test the process.
* Run `qgis-plugin-ci pull-translation --compile <your-transifex-token>`

#### Translating with QT Linguistic (if Transifex not available)

The translation files are in [i18n](../Foursquare/resources/i18n) folder. Translatable content in python files is code
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
* Make a new commit. (`git add -A && git commit -m "Release v0.1.0"`)
* Create new tag for it (`git tag -a v0.1.0 -m "Version v0.1.0"`)
* Push tag to Github using `git push --follow-tags`
* Create Github release
* [qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci) adds release zip automatically as an asset
