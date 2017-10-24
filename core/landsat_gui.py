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
import time
from traits.api import HasTraits, Enum, Date, Button, Str, BaseFloat, Bool, Directory, Int, Property
from traitsui.api import View, Item, UItem, Controller, VGroup, HGroup, TextEditor

from core.download_composer import download_landsat


class LatFloat(BaseFloat):
    def validate(self, obj, name, value):
        if value > 90 or value < -90:
            return self.error(obj, name, value)
        else:
            return value


class LonFloat(BaseFloat):
    def validate(self, obj, name, value):
        if value > 180 or value < -180:
            return self.error(obj, name, value)
        else:
            return value


# here is a gui down in a true MVC pattern.  See passed EOF for shortened form
class LandsatDownloadModel(HasTraits):
    satellite = Enum('LT5', 'LE7', 'LC8')
    start_date = Date
    end_date = Date
    log_txt = Str
    lat = LatFloat
    lon = LonFloat
    latlon_enabled = Bool
    output_path = Directory
    pathrow_enabled = Bool
    path = Int
    row = Int
    download_enabled = Property(depends_on='latlon_enabled, pathrow_enabled')

    def _get_download_enabled(self):
        return self.pathrow_enabled or self.latlon_enabled

    def _latlon_enabled_changed(self, new):
        if new:
            self.pathrow_enabled = False

    def _pathrow_enabled_changed(self, new):
        if new:
            self.latlon_enabled = False

    def do_download(self):
        self._log('starting download start={}, end={}, sat={}'.format(self.start_date, self.end_date, self.satellite))
        kw = {}
        if self.latlon_enabled:
            kw['lat'] = self.lat
            kw['lon'] = self.lon

        if self.output_path:
            kw['output_path'] = self.output_path

        download_landsat(self.start_date, self.end_date, self.satellite, **kw)
        self._log('download finished')

    def _log(self, msg):
        print msg
        msg = '{} - {}'.format(time.time(), msg)
        self.log_txt = '{}{}\n'.format(self.log_txt, msg)


class LandsatController(Controller):
    download_button = Button

    def _download_button_fired(self):
        self.model.do_download()


LANDSAT_VIEW = View(VGroup(VGroup(Item('satellite'), show_border=True, label='General'),
                           HGroup(VGroup(UItem('start_date', style='custom'), show_border=True, label='Start'),
                                  VGroup(UItem('end_date', style='custom'), show_border=True, label='End'))),
                    HGroup(UItem('latlon_enabled'),
                           Item('lat', label='Latitude', enabled_when='latlon_enabled'),
                           Item('lon', label='Longitude', enabled_when='latlon_enabled'),
                           label='LatLon',
                           show_border=True),
                    HGroup(UItem('pathrow_enabled'),
                           Item('path'), Item('row'),
                           show_border=True, label='PathRow'),
                    HGroup(Item('output_path'), show_border=True),
                    UItem('controller.download_button', enabled_when='download_enabled'),
                    VGroup(UItem('log_txt', style='custom',
                                 editor=TextEditor(read_only=True)),
                           show_border=True, label='Log'),
                    resizable=True,
                    width=0.5,
                    title='Configure Landsat Downloader')

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
