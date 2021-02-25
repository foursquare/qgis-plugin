

# Unfolded Studio QGIS plugin
![](https://github.com/UnfoldedInc/qgis-plugin/workflows/Tests/badge.svg)
![](https://github.com/UnfoldedInc/qgis-plugin/workflows/TestsLTR/badge.svg)
[![codecov.io](https://codecov.io/github/UnfoldedInc/qgis-plugin/coverage.svg?branch=master)](https://codecov.io/github/UnfoldedInc/qgis-plugin?branch=master)
![](https://github.com/UnfoldedInc/qgis-plugin/workflows/Release/badge.svg)

<img src="docs/imgs/uf_qgis_logo.svg" width="200" height="200">

This plugin exports a [QGIS](http://qgis.org/) map into a format that can be imported into  [Unfolded Studio](https://studio.unfolded.ai/)  for further analysis or one-click publishing to the web after signing up for a free  [Unfolded](https://unfolded.ai/)  account.

The plugin can also export maps that can be imported into  [kepler.gl](https://kepler.gl/).

# Documentation 
This repository contains a short overview of using the plugin. Full documentation can be found from [docs.unfolded.ai](https://docs.unfolded.ai/)

## Installation
Plugin can be installed via the official QGIS plugin repository. You can access it from QGIS (Plugins --> Manage and Install Plugins). 

You can also install the plugin from a zip package that you can download from the releases of this repository. 

## Using the plugin

Before opening the plugin, a user can add their datasets to QGIS in a normal way (see e.g. [QGIS tutorials](https://www.qgistutorials.com/en/)), do some data processing tasks if necessary and do cartographic styling for the vector layers. 

After the user is satisfied with their result and the plugin has been installed, it can be opened under the *Plugins* tab in QGIS. It opens a new window, where you have the basic export functionalities. 

![Main plugin dialog](docs/imgs/main_dialog.png)

If a project contains multiple layers, user can select which of them should be exported. In the main *Export* tab a user can also select which type of basemap they want to use and which functionalities (e.g. brushing, geocoding) should the interactive map contain. All of these values can be later changed. 

In the *Settings* tab user can define where they want the exported configuration file to be exported on their local disk. A user can also add their personal MapBox API key if they wish to add MapBox basemaps to their project. In this tab a user can also define the logging level in case a 

From the *About* tab a user can see the basic infomation about the version they are using and find relevant links. 

### Supported styling
Currently the plugin supports the following QGIS styles:

 - **Single Symbol with Simple Fill.** These are the basic QGIS styles. The plugin can handle colors for fills and strokes. 
 - **Categorized.** With categorized styling you can visualize qualitative data. 
 - **Graduated.** Graduated styling can be used for sequential or diverging datasets. 

## Development
Contributions are welcome. Refer to [development](docs/development.md) for developing this QGIS3 plugin.

## License
This plugin is licenced with
[GNU Genereal Public License, version 2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html).
See [LICENSE](LICENSE) for more information.
