

# Unfolded Studio QGIS plugin
![](https://github.com/UnfoldedInc/qgis-plugin/workflows/Tests/badge.svg)
![](https://github.com/UnfoldedInc/qgis-plugin/workflows/TestsLTR/badge.svg)
[![codecov.io](https://codecov.io/github/UnfoldedInc/qgis-plugin/coverage.svg?branch=master)](https://codecov.io/github/UnfoldedInc/qgis-plugin?branch=master)
![](https://github.com/UnfoldedInc/qgis-plugin/workflows/Release/badge.svg)

<img src="docs/imgs/uf_qgis_logo.svg" width="200" height="200">

This plugin exports a [QGIS](http://qgis.org/) vector layers into a format that can be imported into  [Unfolded Studio](https://studio.unfolded.ai/)  for further analysis or later one-click publishing to the web after signing up for a free  [Unfolded](https://unfolded.ai/)  account.

The plugin can also export maps that can be imported into [kepler.gl](https://kepler.gl/).

# Documentation 
This readme contains a short overview of basic functionalities of the plugin. Full documentation can be found from [docs.unfolded.ai](https://docs.unfolded.ai/). Plugin has been tested and developed on QGIS version 3.16.x, which is the minimum requirement. 

## Installation
Plugin can be installed via the official QGIS plugin repository and it can be accessed from QGIS (*Plugins --> Manage and Install Plugins*). 

A user can also install the plugin from a zip package that you can download from the releases of this repository. 

## Using the plugin

User can export any vector data format that is [supported in QGIS](https://docs.qgis.org/3.16/en/docs/user_manual/working_with_vector/index.html) and the data can be in any known coordinate reference system as it is reprojected (EPSG:4326) on the fly when the export is done. Layer geometries and styles are exported in to a single JSON configuration file, which can then be imported to Unfolded Studio or kepler.gl. 

Before opening the plugin, a user can add their datasets to QGIS in a normal way (see e.g. [QGIS tutorials](https://www.qgistutorials.com/en/)), do some data processing tasks if necessary and do cartographic styling for the vector layers. After the user is satisfied with their result and the plugin has been installed, it can be opened under the *Plugins* tab in QGIS. It opens a new window, where you have the basic export functionalities. 

![Main plugin dialog](docs/imgs/main_dialog.png)

If a project contains multiple layers, user can select which of them should be exported and which of them will be visible by default. In the main *Export* tab a user can also select which type of basemap they want to use and which functionalities (e.g. brushing, geocoding) should the interactive map contain. All of these values can be later changed. 

In the *Settings* tab user can define where they want the exported configuration file to be exported on their local disk. A user can also add their personal MapBox API key if they wish to add MapBox basemaps to their project. In this tab a user can also define the logging level mainly for development purpose.

From the *About* tab a user can see the basic infomation about the version they are using and find relevant links. 

### Supported styling and layer types
Currently the plugin supports exporting line, point and polygon geometries. The cartographic capabilities in QGIS are vast and can become very complex, so in the first stage of development, the plugin focuses only the basic styles  The following QGIS styles are supported:

 - **Single Symbol with Simple Fill.** These are the basic QGIS styles. With these you can define a fill and a stroke styles (width and color) for a feature. 
 - **Categorized.** With categorized styling you can visualize qualitative data. The color palettes used in QGIS visualization are automatically exported. 
 - **Graduated.** Graduated styling can be used for sequential or diverging datasets. Currently supported classifications are *quantile* and *equal interval*

## Development
If you encounter a bug or would like to see a new feature, please open an issue accordingly. Also other contributions are welcome. Refer to [development](docs/development.md) for developing this QGIS3 plugin.

## License
This plugin is licenced with
[GNU Genereal Public License, version 2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html).
See [LICENSE](LICENSE) for more information.
