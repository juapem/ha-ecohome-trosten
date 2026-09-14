# ha-ecohome

This is a Home Assistant integration for the [New Energy
Eco-Home](https://ehome.ne01.com/) heat pump API, which is used (among others)
by Batavia Heat heat pumps in the Netherlands.

It also works with TROSTEN heat pumps, which are controlled with the same
Eco-Home app. In Uruguay they are sold and supported by [CIR Acondicionamiento
Térmico](https://www.circalefaccion.com/) (Montevideo); see CIR's [heat pump
catalogue](https://tienda.circalefaccion.com/products/bombas_de_calor/calefaccion/BC01CAL01/1).

## Installation

You can install this repo via HACS or by copying the integration files yourself.
I'd recommend using HACS.

### Installation via HACS

First, install HACS using these instructions: https://hacs.xyz/docs/use/download/download/

Then, activate HACS using these instructions: https://hacs.xyz/docs/use/configuration/basic/

After this, you can search for Eco-Home, and download and install
from there.

If you need to add this repository as a custom repository for whichever reason,
you can do so with the following settings:

- Repository: https://github.com/sgielen/ha-ecohome
- Type: Integration

### Installing yourself

Alternatively, you can copy the `custom_components/ecohome` directory from this
repository directly into your `config/custom_components` directory inside Home
Assistant.

### Configuration

After installation, you can add the integration inside Home Assistant settings
-> Devices and Services, search for Eco-Home.  This requires your username and
password. If you have only one device, it is immediately added; if you have
multiple you can select which ones to add.  Devices shared with you cannot be
added yet, but this is probably an easy fix.

### Options

Once added, click **Configure** on the integration to change:

- **Update interval (minutes)**: how often the heat pump is polled (1–30).
- **Language of sensor names**: the language in which the Eco-Home API returns
  the names of sensors and parameters. Available: English, Español, Deutsch,
  Français, Italiano, Português (Portugal) and Português (Brasil).

If you don't choose a language, the integration uses Home Assistant's language
when the API supports it, and English otherwise. The `ecohome` library always
requests Dutch (`nl_NL`), for which the API has no parameter name translations
and returns them in Portuguese, so Dutch is not offered. Logging in still uses
Dutch, because the library recognizes a wrong password by its error message.

Changing the language reloads the integration and renames the sensors; their
entity IDs stay the same, so automations and dashboards keep working.

## Development

### Running tests

This project uses `uv` for dependency management and `pytest` for testing.

- Install dependencies: `uv sync`
- Run the test suite: `uv run pytest`

### Releases

- Update version number in `pyproject.toml` and
  `custom_components/ecohome/manifest.json`. I try to keep the version
  number in sync with the Python `ecohome` library if possible.
- Run `uv sync`, commit and push all changes
- Create a tag and github release: `gh release create v0.1.2 --title "v0.1.2" --generate-notes`
- The new version should be indexed by HACS automatically.
