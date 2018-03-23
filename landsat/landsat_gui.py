# ===============================================================================
# Copyright 2017 ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================
from traits.api import HasTraits, Enum, Date, Button
from traitsui.api import View, Item, UItem, Controller

from .download_composer import download_landsat


# here is a gui down in a true MVC pattern.  See passed EOF for shortened form
class LandsatDownloadModel(HasTraits):
    satellite = Enum('LT5', 'LE7', 'LC8')
    start_date = Date
    end_date = Date

    def do_download(self):
        download_landsat(self.start_date, self.end_date, self.satellite)


class LandsatController(Controller):
    download_button = Button

    def _download_button_fired(self):
        self.model.do_download()


LANDSAT_VIEW = View(Item('start_date', style='custom'),
                    Item('end_date', style='custom'),
                    Item('satellite'),
                    Item('controller.download_button'),
                    title='Configure Landsat Downloader',
                    buttons=['OK', 'Cancel'])

if __name__ == '__main__':
    m = LandsatDownloadModel()
    c = LandsatController(model=m)

    c.configure_traits(view=LANDSAT_VIEW)

# ============= EOF =============================================
#
# class Downloader(HasTraits):
#     satellite = Enum('LT5', 'LE7', 'LC8')
#     start_date = Date
#     end_date = Date
#     download_button = Button
#
#     def do_download(self):
#         download_landsat(self.start_date, self.end_date, self.satellite)
#
#     def _download_button_fired(self):
#         self.do_download()
#
#     def traits_view(self):
#         v = View(Item('start_date', style='custom'),
#                  Item('end_date', style='custom'),
#                  Item('satellite'),
#                  Item('download_button'),
#                  title='Configure Landsat Downloader',
#                  buttons=['OK', 'Cancel'])
#
#         return v
#
#
# if __name__ == '__main__':
#     d = Downloader()
#     d.configure_traits()