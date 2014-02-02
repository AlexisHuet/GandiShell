#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Stuffs to represent a disk image."""

from gandishell.objects import DataObject

from gandishell.utils import APIKEY, ask_string, info, warning, catch_fault


class Image(DataObject):
    """The image itself."""

    class_token = ['list']
    instance_token = ['info']
    all_token = class_token + instance_token

    ############# classmethods #############
    @classmethod
    def list(cls, api):
        """Get a list of existing disks images."""
        res = {}
        for image in api.hosting.image.list(APIKEY):
            res[image['id']] = Image(**image)
        return res

    @classmethod
    def filter(cls, api, datacenter_id):
        """Select an image by filtering on his name."""
        images = {k: v for k, v in cls.list(api).items()
                    if v['datacenter_id']  == datacenter_id}
        for k, v in images.items():
            print(k, v)
        while(len(images) > 1):
            _ = "an id or a keyword, as we still have {} possible disk images."
            keyword = ask_string(_.format(len(images)), '')
            try :
                keyword = int(keyword)
                if keyword not in images:
                    warning("{} is not a valid id".format(keyword))
                else:
                    image = images[keyword]
                    break
            except ValueError:
                filtered = {k: v for k, v in images.items()
                            if keyword in v['label']}
                if not len(filtered):
                    warning("No label contains \"{}\"".format(keyword))
                    continue
                elif len(filtered) is 1:
                    image = filtered.popitem()[1]
                    break
                else:
                    images = filtered
                    for _, v in images.items():
                        print(v)
                    continue
        info('Image selected :')
        print(image)
        return image['disk_id']

    ########### id only commands ###########
    def info(self, api):
        """Get info about this disk image."""
        info("Info about Image {}".format(self['id']))
        with catch_fault():
            res = api.hosting.image.info(APIKEY, self['id'])
        return Image(**res)
