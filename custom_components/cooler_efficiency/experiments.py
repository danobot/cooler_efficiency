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
from homeassistant.components.notify import (ATTR_MESSAGE, DOMAIN as DOMAIN_NOTIFY)
from .const import *

def experiment_finished(self):
    self.logger.debug("Experiment finished")
    self.currentSnapshot = self.take_snapshot()
    effDelta =  self.currentSnapshot["state"] - self.previousSnapshot["state"]
    result = []
    if effDelta > 0:
        result.append("The efficiency increased by %f percent!" % (effDelta))
    else:
        result.append("The efficiency decreased by %f percent. Fail." % (effDelta))

    tempDelta =  self.currentSnapshot["indoor_temp"] - self.previousSnapshot["indoor_temp"]
    if tempDelta < 0:
        result.append("The indoor temperature decreased by %f degrees!" % (tempDelta))
    else:
        result.append("The indoor temperature increased by %f degrees. Fail." % (tempDelta))

    humDelta =  self.currentSnapshot["indoor_hum"] - self.previousSnapshot["indoor_hum"]
    result.append("The indoor hum changed by %f." % (humDelta))

    message = '\n'.join(result)
    self.data["experiments"].append({
        "previous": self.previousSnapshot,
        "current": self.currentSnapshot,
        "efficiencyDelta": effDelta,
        "tempDelta": tempDelta,
        "humDelta": humDelta
    })
    self.logger.debug("Experiment outcome: " + message)
    self.data[RESULT] = message
    self.notify(self.experimentNotifier, message)
