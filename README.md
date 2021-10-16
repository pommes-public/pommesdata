# pommesdata

**A full-featured transparent data preparation routine from raw data to POMMES model inputs**

This is the **data preparation routine** of the fundamental power market model *POMMES* (**PO**wer **M**arket **M**odel of **E**nergy and re**S**ources).<br>
Please navigate to the section of interest to find out more.

## Contents
* [Introduction](#introduction)
* [Documentation](#documentation)
* [Installation and usage](#installation-and-usage)
* [Contributing](#contributing)
* [Citing](#citing)
* [License](#license)

## Introduction
*POMMES* itself is a cosmos consisting of a **dispatch model**, a **data preparation routine** (stored in this repository and described here) and an **investment model** for the German wholesale power market. The model was originally developed by a group of researchers and students at the [chair of Energy and Resources Management of TU Berlin](https://www.er.tu-berlin.de/menue/home/) and is now maintained by a group of alumni and open for other contributions.

If you are interested in the actual dispatch or investment model, please find more information here:
- [pommesdispatch](https://github.com/pommes-public/pommesdispatch): A bottom-up fundamental power market model for the German electricity sector
- pommesinvest: A multi-period integrated investment and dispatch model for the German power sector (upcoming).

## Documentation
The data preparation is mainly carried out in this **[jupyter notebook](https://github.com/pommes-public/pommesdata/blob/dev/pommesdata/data_preparation.ipynb)**.
The data sources used as well as the calculation and transformation steps applied are described in a transparent manner.
In addition to that, there is a **[documentation of pommesdata](https://pommesdata.readthedocs.io/)** on readthedocs.
This in turn contains a documentation of the functions and classes used for data preparation. 

## Installation and usage
There are **two use cases** for using `pommesdata`:
1. Using readily prepared output data sets as `pommesdispatch` or `pommesinvest` inputs
2. Understanding and manipulating the data prep process (inspecting / developing)

If you are only interested in the readily prepared data sets (option 1), you can obtain
them from zenodo and download it here: [https://zenodo.org/](https://zenodo.org/)

If you are interested in understanding the data preparation process itself or
if you wish to include own additions, changes or assumptions, you can
[fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo)
 and then clone the repository, in order to copy the files locally by typing

```
git clone https://github.com/pommes-public/pommesdata.git
```

After cloning the repository, you have to install the required dependencies.
Make sure you have conda installed as a package manager.
If not, you can download it [here](https://www.anaconda.com/).
Open a command shell and navigate to the folder where you copied the environment to. Use the following command to install dependencies

```
conda env create -f environment.yml
```
Activate your environment by typing
```
conda activate pommes_data
```

## Contributing
Every kind of contribution or feedback is warmly welcome.<br>
We use the GitHub issue management as well as pull requests for collaboration. 

We try to stick to the PEP8 coding standards.

The jupyter notebook for the data preparation does not (necessarily have to) 
meet PEP8 standards, though readability should be made sure.

The following people have contributed in the following manner to `pommesdata`:

| Name | Contribution | Status |
| ---- | ---- | ---- |
| Yannick Werner | major development & conceptualization<br>conceptualization, main data preparation routines (status quo data for all components, detailed RES, interconnector and hydro data), architecture | coordinator & maintainer,<br>developer & corresponding author |
| Johannes Kochems | major development & conceptualization<br>conceptualization, co-development of main data preparation routines (esp. future projection for all components, RES tender data and LCOE estimates, documentation), architecture publishing process | coordinator & co-maintainer,<br>developer & corresponding author |
| Leticia Encinas Rosa | development<br>early-stage contributions to conventional power plant data collection for Germany (technical data, data processing routines) | former developer (research associate) |
| Carla Spiller | development<br>early-stage contributions to conventional power plant data collection for Germany (technical data, data processing routines) | former developer (student assistant) |
| Sophie Westphal | development<br>contributions to cost data collection for conventional plants (data bundling and processing routines) | former developer (student assistant) |
| Julian Endres | development<br>early-stage contributions to conventional power plant data collection for Germany (location, technical data) | former developer (student assistant) |
| Julien Faist | development<br>contributions to conventional power plant data collection for Germany (shutdowns, new constructions) | former developer (master's student) |
| Timona Ghosh | development<br>early-stage development of interconnector exchange (approach and data) | former developer (master's student) |
| Johannes Giehl | development<br>conceptualization and data licensing information | developer |
| Christian Fraatz | development<br>early-stage contributions to European conventional power plant data (location and data processing) | former developer (bachelor's student) |
| Robin Claus | development<br>early-stage contributions to German conventional power plant data (efficiencies) | former developer (student assistant) |
| Daniel Peschel | development<br>early-stage input data contribution to German conventional power plant data (CHP information) | former developer (master's student) |
| Conrad Nicklisch | development<br>early-stage contribution to RES cost information | former developer (bachelor's student) |
| Benjamin Grosse | development<br>early-stage contributions to conventional power plants data & support | developer |
| Joachim Müller-Kirchenbauer | support & conceptualization<br>early-stage conceptualization, funding | supporter (university professor) |

*Note: Not every single contribution is reflected in the current version of
`pommesdata`. This is especially true for those marked as early-stage 
contributions that may have been extended, altered or sometimes discarded. 
Nonetheless, all people listed have made valuable contributions. The ones
discarded might be re-integrated at some point in time.
Dedicated contributions to `pommesdispatch` and `pommesinvest` are not included
in the list, but listed individually for these projects.*

## Citing
A publication using and introducing `pommesdispatch` is currently in preparation.
This in turn will make use of data collected with `pommesdata`.

Data sets created with `pommesdata` are shared at [zenodo](https://zenodo.org).
If you use these, please refer to the citation information given at zenodo.

If you are using `pommesdata` for your own analyses, we recommend citing as:<br>
*Werner, Y.; Kochems, J. et al. (2021): pommesdata. A full-featured transparent data preparation routine from raw data to POMMES model inputs. https://github.com/pommes-public/pommesdata, accessed YYYY-MM-DD.*

We furthermore recommend naming the version tag or the commit hash used for the sake of transparency and reproducibility.

Also see CITATION.cff for citation information. Licensing information stated
in the CITATION.cff is only applicable for the code itself, see 
[license](#License).

## License
Licensing for the code - in the following referred to as software - 
and the input data used differs. For the licensing of the data, 
please see the detailed list of data sets below.

### Software (code)

Copyright 2021 pommes developer group

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### Data (input data)
The following table contains the primary data sources used to create data sets used for *POMMES* models.
The licensing of the different sources differs and the table should provide an overview over the licences used.
Thus, we cannot publish all the data under an open license, such as a Creative Commons Attribution license. Please
be aware that some data might be subject to copyright.

| institution | data set | license | distributed with the repository | download link |
| ---- | ---- | ---- | ---- | ---- |
| OPSD | data package conventional power plants | MIT License for software; for dataset-specific license see hyperlink | yes | https://doi.org/10.25832/conventional_power_plants/2018-12-20 
| ÜNB / BNetzA | power plant list | free to use, license-free according to §5 Abs. 1 UrhG | yes | https://www.netzentwicklungsplan.de/sites/default/files/paragraphs-files/Kraftwerksliste_%C3%9CNB_Entwurf_Szenariorahmen_2030_V2019_2_0_0.pdf
| FZJ / KIT / FIAS | FRESNA (PyPSA-EUR) PP matching | GPLv3 for software, for dataset-specific license see hyperlink | yes | https://doi.org/10.5281/zenodo.3358985
| tmrowco | bidding zone geometries | MIT License | yes | https://github.com/tmrowco/electricitymap-contrib/pull/1383
| UBA | new-built power plants | usage of data accordant to § 12a EGovG permitted | yes | https://www.umweltbundesamt.de/sites/default/files/medien/384/bilder/dateien/4_tab_genehmigte-in_genehmigung-kraftwerksprojekte_2019-04-04.pdf
| BDEW | new-built power plants | All rights reserved | yes | https://www.bdew.de/media/documents/PI_20190401_BDEW-Kraftwerksliste.pdf
| BNetzA | new-built & decommissioned power plants | free to use, license-free according to §5 Abs. 1 UrhG | yes | https://www.bundesnetzagentur.de/DE/Sachgebiete/ElektrizitaetundGas/Unternehmen_Institutionen/Versorgungssicherheit/Erzeugungskapazitaeten/Kraftwerksliste/kraftwerksliste-node.html
| Energie SaarLorLux | new-built power plant | All rights reserved | yes | https://www.energie-saarlorlux.com/unternehmen/mehr-gutes-klima/unsere-co2-projekte/
| ENTSOE | new-built power plants | CC BY 4.0 | yes | https://tyndp.entsoe.eu/maps-data
| BNetzA | threshold for new-built power plants | free to use, license-free according to §5 Abs. 1 UrhG | yes | https://www.bundesnetzagentur.de/SharedDocs/Downloads/DE/Sachgebiete/Energie/Unternehmen_Institutionen/Versorgungssicherheit/Berichte_Fallanalysen/BNetzA_Netzstabilitaetsanlagen13k.pdf?__blob=publicationFile&v=3
| DIW | efficiency estimates for power plants | All rights reserved | yes | https://www.diw.de/documents/publikationen/73/diw_01.c.440963.de/diw_datadoc_2014-072.pdf
| BNetzA | power plants shutdown | free to use, license-free according to §5 Abs. 1 UrhG | yes | https://www.bundesnetzagentur.de/DE/Sachgebiete/ElektrizitaetundGas/Unternehmen_Institutionen/Versorgungssicherheit/Erzeugungskapazitaeten/KWSAL/KWSAL
| juris | nuclear power plants shutdown | free to use, license-free according to §5 Abs. 1 UrhG | yes | https://www.gesetze-im-internet.de/atg/
| juris | coal power plants shutdown | free to use, license-free according to §5 Abs. 1 UrhG | yes | https://www.gesetze-im-internet.de/kvbg/index.html
| KWSB | coal power plants shutdown | CC BY-ND 3.0 DE | yes | https://www.bmwi.de/Redaktion/DE/Downloads/A/abschlussbericht-kommission-wachstum-strukturwandel-und-beschaeftigung.pdf?__blob=publicationFile
| ENTSOE | Actual Generation per Generation Unit | Use pursuant to Article 5 of the Terms & Conditions of ENTSO-E; data owned by the specific TSOs | no | https://transparency.entsoe.eu/generation/r2/actualGenerationPerGenerationUnit/show
| ENTSOE | Water Reservoirs and Hydro Storage Plants | Use pursuant to Article 5 of the Terms & Conditions of ENTSO-E; data owned by the specific TSOs | no | https://transparency.entsoe.eu/generation/r2/waterReservoirsAndHydroStoragePlants/show
| ENTSOE | Actual Generation per Production Type | Use pursuant to Article 5 of the Terms & Conditions of ENTSO-E; data owned by the specific TSOs | no | https://transparency.entsoe.eu/generation/r2/actualGenerationPerGenerationUnit/show
| UBA | specific emission factors | Use pursuant to § 12a EGovG for pre-calculations | yes | https://www.umweltbundesamt.de/publikationen/entwicklung-der-spezifischen-kohlendioxid-6
| OPSD | time series data | MIT License for software; for dataset-specific license see hyperlink | yes | https://data.open-power-system-data.org/time_series/2020-10-06
| ÜNB | Anlagenstammdaten | data owned by the German TSO | yes | https://www.netztransparenz.de/EEG/Anlagenstammdaten
| ÜNB | EEG-Bewegungsdaten zur Jahresabrechnung 2017 | data owned by the German TSO | yes | https://www.netztransparenz.de/EEG/Jahresabrechnungen
| IRENA | installed RES capacities | All rights reserved, data used for pre-calculations | no | https://www.irena.org/Statistics/Download-Data
| ENTSO-E | Installed Capacity per Production Type | Use pursuant to Article 5 of the Terms & Conditions of ENTSO-E; data owned by the specific TSOs | no | https://transparency.entsoe.eu/generation/r2/installedGenerationCapacityAggregation/show
| Prognos et al. | study on RES capacities for DE | All rights reserved, data used for pre calculations | yes | https://www.agora-energiewende.de/veroeffentlichungen/klimaneutrales-deutschland/
| BNetzA | RES tender results solarPV | free to use, license-free according to §5 Abs. 1 UrhG | yes | https://www.bundesnetzagentur.de/DE/Sachgebiete/ElektrizitaetundGas/Unternehmen_Institutionen/Versorgungssicherheit/Erzeugungskapazitaeten/Kraftwerksliste/kraftwerksliste-node.html
| BNetzA | RES tender results wind onshore | free to use, license-free according to §5 Abs. 1 UrhG | yes | https://www.bundesnetzagentur.de/DE/Sachgebiete/ElektrizitaetundGas/Unternehmen_Institutionen/Ausschreibungen/Wind_Onshore/BeendeteAusschreibungen/BeendeteAusschreibungen_node.html
| BNetzA | RES tender results common tenders | free to use, license-free according to §5 Abs. 1 UrhG | yes | https://www.bundesnetzagentur.de/DE/Sachgebiete/ElektrizitaetundGas/Unternehmen_Institutionen/Ausschreibungen/Wind_Onshore/BeendeteAusschreibungen/BeendeteAusschreibungen_node.html
| BNetzA | RES tender results offshore | free to use, license-free according to §5 Abs. 1 UrhG | yes | https://www.bundesnetzagentur.de/DE/Service-Funktionen/Beschlusskammern/1_GZ/BK6-GZ/2017/BK6-17-001/Ergebnisse_erste_Ausschreibung.pdf?__blob=publicationFile&v=3
| BNetzA | RES tender results offshore | free to use, license-free according to §5 Abs. 1 UrhG | yes | https://www.bundesnetzagentur.de/DE/Service-Funktionen/Beschlusskammern/1_GZ/BK6-GZ/2018/BK6-18-001/Ergebnisse_zweite_ausschreibung.pdf?__blob=publicationFile&v=3
| BNetzA | solarPV installations (and remuneration) | free to use, license-free according to §5 Abs. 1 UrhG | yes | https://www.bundesnetzagentur.de/DE/Sachgebiete/ElektrizitaetundGas/Unternehmen_Institutionen/ErneuerbareEnergien/ZahlenDatenInformationen/EEG_Registerdaten/ArchivDatenMeldgn/ArchivDatenMeldgn_node.html
| ÜNB | capacity balance | All rights reserved, data used for pre-calculations | yes | https://www.netztransparenz.de/portals/1/Bericht_zur_Leistungsbilanz_2019.pdf
| DIW | fuel costs uranium 2017 | All rights reserved | yes | https://www.diw.de/documents/publikationen/73/diw_01.c.440963.de/diw_datadoc_2014-072.pdf
| DIW | operation costs | All rights reserved | yes | https://www.diw.de/documents/publikationen/73/diw_01.c.440963.de/diw_datadoc_2014-072.pdf
| Öko Institut | fuel costs lignite 2017 | All rights reserved | yes | https://www.oeko.de/oekodoc/1995/2014-015-de.pdf
| Destatis | fuel costs hardcoal 2017 | CC BY 2.0 DE | yes | https://www-genesis.destatis.de/genesis/online?&sequenz=tabelleErgebnis&selectionname=43511-0001#abreadcrumb
| BAFA | fuel costs natural gas 2017 | CC BY-ND 3.0 DE | yes | https://www.bafa.de/SharedDocs/Downloads/DE/Energie/egas_aufkommen_export_1991.html
| BMWI | fuel costs heating oil 2017 | CC BY-ND 3.0 DE | yes | https://www.bmwi.de/Redaktion/DE/Artikel/Energie/energiedaten-gesamtausgabe.html
| r2b | transport costs | CC BY-ND 3.0 DE | yes | https://www.bmwi.de/Redaktion/DE/Publikationen/Studien/definition-und-monitoring-der-versorgungssicherheit-an-den-europaeischen-strommaerkten.pdf?__blob=publicationFile&v=18
| Fraunhofer ISI | operation costs | All rights reserved | yes | https://www.ise.fraunhofer.de/content/dam/ise/de/documents/publications/studies/DE2018_ISE_Studie_Stromgestehungskosten_Erneuerbare_Energien.pdf

### Prepared data sets (data sets created with *pommesdata*)
Please refer to the licensing information provided at [zenodo](https://zenodo.org)