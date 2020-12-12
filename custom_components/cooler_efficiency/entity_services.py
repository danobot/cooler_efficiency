"""
This file is part of Cooler Efficiency.

Cooler Efficiency is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Cooler Efficiency is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Cooler Efficiency.  If not, see <https://www.gnu.org/licenses/>.

"""
import voluptuous as vol
from threading import Timer


import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.config_validation import (  # noqa: F401
    make_entity_service_schema,
)


from .const import (
  SERVICE_START_EXPERIMENT
)


def async_setup_entity_services(component: EntityComponent):
    """ Setup Entity services."""

    component.logger.debug("Setting up entity services")    
    component.async_register_entity_service(SERVICE_START_EXPERIMENT, {}, "async_start_experiment")

    return True




def async_entity_service_start_experiment(self):
    if self.timer_handle and self.timer_handle.is_alive():
        self.logger.debug("Existing experiment in progress.")
        self.notify(self.experimentNotifier, "Existing experiment in progress.")
    else:
        self.notify(self.experimentNotifier, "Starting new AC experiemnt")
        self.logger.debug("Starting new AC experiemnt: ")
        self.timer_handle = Timer(300, self.experiment_finished)
        self.previousSnapshot = self.take_snapshot()
        self.timer_handle.start()
