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




def experiment_finished(self):
    self.logger.debug("Experiment finished")
    self.currentSnapshot = self.take_snapshot()
    effDelta =  self.currentSnapshot["state"] - self.previousSnapshot["state"]
    if effDelta > 0:
        self.logger.debug("The efficiency increased by %f degrees!" % (effDelta))
    else:
        self.logger.debug("The efficiency decreased by %f degrees. Fail." % (effDelta))

    tempDelta =  self.currentSnapshot["indoor_temp"] - self.previousSnapshot["indoor_temp"]
    if tempDelta < 0:
        self.logger.debug("The indoor temperature decreased by %f degrees!" % (tempDelta))
    else:
        self.logger.debug("The indoor temperature increased by %f degrees. Fail." % (tempDelta))
