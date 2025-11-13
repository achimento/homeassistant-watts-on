# Watts On - Water & Heating Integration
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

The `watts-on` component is a Home Assistant custom component for monitoring your personal water and heating usage from the Watts On app.


# Installation


### Manual Installation
  1. Copy watts-on folder into your custom_components folder in your hass configuration directory.
  2. Restart Home Assistant.
  3. Configure the integration.


### Installation with HACS (Home Assistant Community Store)
Eventually this will become an official HACS integration, for now use the custom repo method.
  1. Open HACS and click the 3 dots in upper right corner.
  2. Type in https://github.com/achimento/homeassistant-watts-on as the name, and choose integration as the type.
  3. Restart Home Assistant.
  4. Add the Integration and configure.


### Configuration & Requirements
- Have a user on the Watts On app created with username/password.
- Connect Watts On to your heating and water provider using the app.


# Notice on integration status


### Purpose
The Purpose of this Home Assistant integration is to allow people to see their personal water and heating usage without having to rely on hardware.\
This will not work for everyone as it relies on Watts On having an integration to your water/heating provider.\
The concept here is that people should be able to automatically pull their water and heating data as easily as possible.\
Generally I do not like that ones personal data is not readily available. Ideally there would be a service at some point similar to eloverblik.dk. First thought was using developer.watts.dk, but the API is severely lacking.\
The inspiration for this project is from a specific issue from another project with a similar purpose: [homeassistant-novafos ISSUE](https://github.com/kpoppel/homeassistant-novafos/issues/10)\
**Disclaimer:** I have tried talking to both Watts, utility comanies, etc. about access to an official api, but to no avail. As such I have ended up with a solution of reverse engineering the API for the Watts On app using a https proxy, as I had no other options of getting the data in an automated manner.

### Current progress
- Azure AD PKCE Auth flow (Used in Watts On) has been automated in a private github Repo. Works with both access and refresh tokens.
- Water and Heating data pulling has been set up and functions as expected in a private github repo
- Cleaned up the functions and changed the structure to work with Home Assistant/HACS, slowly adding code to this repository.
- Automatic fetch of meter ids, both heating and water
- Add HASS Statistics sensor to allow easy graph display of usage data.
- COMING "SOON": Add Migration based logic for version updates of the integration
- COMING "SOON": Add sample images and example usage in the readme
- COMING "SOON": Add tests for robustness
- COMING "SOON": Add Validation during config flow set up.
- Maybe more?
