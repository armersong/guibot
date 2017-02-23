# Copyright 2013 Intranet AG / Plamen Dimitrov and Thomas Jarosch
#
# guibender is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# guibender is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with guibender.  If not, see <http://www.gnu.org/licenses/>.
#

import re
import os
try:
    import configparser as config
except ImportError:
    import ConfigParser as config
import logging
log = logging.getLogger('guibender.settings')

import PIL.Image
from tempfile import NamedTemporaryFile

# TODO: make this OpenCV independent with the rest
import cv2

from errors import *
import inputmap


class Settings(type):
    """
    Metaclass used for the definition of static properties (the settings).

    We overwrite the name of the class in order to avoid documenting
    all settings here and adding an empty actual class. Instead, the resulting
    documentation contains just the settings class (using this as metaclass)
    and all settings respectively. In this way the front user should not worry
    about such implementation detail and simply use the provided properties.

    For those that like to think about it nonetheless: All methods of the
    resulting settings class are therefore static since they are methods of
    a class object, i.e. a metaclass instance.
    """

    # operational parameters shared between all instances
    _click_delay = 0.1
    _drag_delay = 0.5
    _drop_delay = 0.5
    _keys_delay = 0.2
    _type_delay = 0.1
    _rescan_speed_on_find = 0.2
    _screen_autoconnect = True
    _preprocess_special_chars = True
    _save_needle_on_error = True
    _image_logging_level = logging.ERROR
    _image_logging_destination = "./imglog"
    _image_logging_step_width = 3
    _image_quality = 3

    # backends shared between all instances
    _desktop_control_backend = "autopy"
    _find_image_backend = "hybrid"
    _template_match_backend = "ccoeff_normed"
    _feature_detect_backend = "ORB"
    _feature_extract_backend = "ORB"
    _feature_match_backend = "BruteForce-Hamming"

    def click_delay(self, value=None):
        """
        Getter/setter for property attribute.

        :param value: time interval between two clicks in a double click
        :type value: float or None
        :returns: current value if no argument was passed otherwise only sets it
        :rtype: float or None
        """
        if value is None:
            return Settings._click_delay
        else:
            Settings._click_delay = value
    #: time interval between two clicks in a double click
    click_delay = property(fget=click_delay, fset=click_delay)

    def delay_after_drag(self, value=None):
        """
        Same as :py:func:`Settings.click_delay` but with

        :param value: timeout before drag operation
        """
        if value is None:
            return Settings._drag_delay
        else:
            Settings._drag_delay = value
    #: timeout before drag operation
    delay_after_drag = property(fget=delay_after_drag, fset=delay_after_drag)

    def delay_before_drop(self, value=None):
        """
        Same as :py:func:`Settings.click_delay` but with

        :param value: timeout before drop operation
        """
        if value is None:
            return Settings._drop_delay
        else:
            Settings._drop_delay = value
    #: timeout before drop operation
    delay_before_drop = property(fget=delay_before_drop, fset=delay_before_drop)

    def delay_before_keys(self, value=None):
        """
        Same as :py:func:`Settings.click_delay` but with

        :param value: timeout before key press operation
        """
        if value is None:
            return Settings._keys_delay
        else:
            Settings._keys_delay = value
    #: timeout before key press operation
    delay_before_keys = property(fget=delay_before_keys, fset=delay_before_keys)

    def delay_between_keys(self, value=None):
        """
        Same as :py:func:`Settings.click_delay` but with

        :param value: time interval between two consecutively typed keys
        """
        if value is None:
            return Settings._type_delay
        else:
            Settings._type_delay = value
    #: time interval between two consecutively typed keys
    delay_between_keys = property(fget=delay_between_keys, fset=delay_between_keys)

    def rescan_speed_on_find(self, value=None):
        """
        Same as :py:func:`Settings.click_delay` but with

        :param value: time interval between two image matching attempts
                      (used to reduce overhead on the CPU)
        """
        if value is None:
            return Settings._rescan_speed_on_find
        else:
            Settings._rescan_speed_on_find = value
    #: time interval between two image matching attempts (used to reduce overhead on the CPU)
    rescan_speed_on_find = property(fget=rescan_speed_on_find, fset=rescan_speed_on_find)

    def screen_autoconnect(self, value=None):
        """
        Getter/setter for property attribute.

        :param value: whether to perform complete initialization of the
                      desktop control backend
        :type value: bool or None
        :returns: current value if no argument was passed otherwise only sets it
        :rtype: bool or None
        :raises: :py:class:`ValueError` is value is not boolean or None

        Complete initialization includes connecting to the backend (screen)
        selected in the `_desktop_control_backend`.

        If disabled, you have to connect before performing any GUI operations::

            region.dc_backend.connect_screen()

        The use of this is to allow you to perform some configuration first.
        """
        if value is None:
            return Settings._screen_autoconnect
        elif value == True or value == False:
            Settings._screen_autoconnect = value
        else:
            raise ValueError
    #: whether to perform complete initialization of the desktop control backend
    screen_autoconnect = property(fget=screen_autoconnect, fset=screen_autoconnect)

    def preprocess_special_chars(self, value=None):
        """
        Same as :py:func:`Settings.screen_autoconnect` but with

        :param value: whether to preprocess capital and special characters and
                      handle them internally

        .. warning:: The characters will be forcefully preprocessed for the
            autopy on linux (capital and special) and vncdotool (capital) backends.
        """
        if value is None:
            return Settings._preprocess_special_chars
        elif value == True or value == False:
            Settings._preprocess_special_chars = value
        else:
            raise ValueError
    #: whether to preprocess capital and special characters and handle them internally
    preprocess_special_chars = property(fget=preprocess_special_chars, fset=preprocess_special_chars)

    def save_needle_on_error(self, value=None):
        """
        Same as :py:func:`Settings.screen_autoconnect` but with

        :param value: whether to perform an extra needle dump on matching error
        """
        if value is None:
            return Settings._save_needle_on_error
        elif value == True or value == False:
            Settings._save_needle_on_error = value
        else:
            raise ValueError
    #: whether to perform an extra needle dump on matching error
    save_needle_on_error = property(fget=save_needle_on_error, fset=save_needle_on_error)

    def image_logging_level(self, value=None):
        """
        Getter/setter for property attribute.

        :param value: logging level similar to the python logging module
        :type value: int or None
        :returns: current value if no argument was passed otherwise only sets it
        :rtype: int or None

        .. seealso:: See the image logging documentation for more details.
        """
        if value is None:
            return Settings._image_logging_level
        else:
            Settings._image_logging_level = value
    #: logging level similar to the python logging module
    image_logging_level = property(fget=image_logging_level, fset=image_logging_level)

    def image_logging_step_width(self, value=None):
        """
        Same as :py:func:`Settings.image_logging_level` but with

        :param value: number of digits when enumerating the image
                      logging steps, e.g. value=3 for 001, 002, etc.
        """
        if value is None:
            return Settings._image_logging_step_width
        else:
            Settings._image_logging_step_width = value
    #: number of digits when enumerating the image logging steps, e.g. value=3 for 001, 002, etc.
    image_logging_step_width = property(fget=image_logging_step_width, fset=image_logging_step_width)

    def image_quality(self, value=None):
        """
        Same as :py:func:`Settings.image_logging_level` but with

        :param value: quality of the image dumps ranging from 0 for no compression
                      to 9 for maximum compression (used to save space and reduce
                      the disk space needed for image logging)
        """
        if value is None:
            return Settings._image_quality
        else:
            Settings._image_quality = value
    #: quality of the image dumps ranging from 0 for no compression to 9 for maximum compression
    # (used to save space and reduce the disk space needed for image logging)
    image_quality = property(fget=image_quality, fset=image_quality)

    def image_logging_destination(self, value=None):
        """
        Getter/setter for property attribute.

        :param value: relative path of the image logging steps
        :type value: str or None
        :returns: current value if no argument was passed otherwise only sets it
        :rtype: str or None
        """
        if value is None:
            return Settings._image_logging_destination
        else:
            Settings._image_logging_destination = value
    #: relative path of the image logging steps
    image_logging_destination = property(fget=image_logging_destination, fset=image_logging_destination)

    def desktop_control_backend(self, value=None):
        """
        Same as :py:func:`Settings.image_logging_destination` but with

        :param value: name of the desktop control backend
        :raises: :py:class:`ValueError` if value is not among the supported backends

        Supported backends:
           * autopy - Windows, Linux (and OS X) compatible with both the GUI
                      actions and their calls executed on the same machine.
           * qemu - guest OS independent with GUI actions on a virtual machine
                    through Qemu Monitor object (provided by Autotest) and
                    their calls on the host machine.
           * vncdotool - guest OS independent or Linux remote OS with GUI
                         actions on a remote machine through vnc and their
                         calls on a vnc client machine.

        .. warning:: To use a particular backend you need to satisfy its dependencies,
            i.e. the backend has to be installed or you will have unsatisfied imports.
        """
        if value is None:
            return Settings._desktop_control_backend
        else:
            if value not in ["autopy", "qemu", "vncdotool"]:
                raise ValueError("Unsupported backend for GUI actions '%s'" % value)
            Settings._desktop_control_backend = value
    #: name of the desktop control backend
    desktop_control_backend = property(fget=desktop_control_backend, fset=desktop_control_backend)

    # these methods do not check for valid values since this
    # is already done at the equalizer on initialization
    def find_image_backend(self, value=None):
        """
        Same as :py:func:`Settings.image_logging_destination` but with

        :param value: name of the computer vision backend

        Supported backends:
            * template - template matching using correlation coefficients,
                         square difference or the default autopy matching.
            * feature - feature matching using a mixture of feature detection,
                        extraction and matching algorithms.
            * hybrid - a mixture of template and feature matching where the
                       first is used as necessary and the second as sufficient stage.

        .. warning:: To use a particular backend you need to satisfy its dependencies,
            i.e. the backend has to be installed or you will have unsatisfied imports.
        """
        if value is None:
            return Settings._find_image_backend
        else:
            Settings._find_image_backend = value
    #: name of the computer vision backend
    find_image_backend = property(fget=find_image_backend, fset=find_image_backend)

    def template_match_backend(self, value=None):
        """
        Same as :py:func:`Settings.image_logging_destination` but with

        :param value: name of the template matching backend

        Supported backends: autopy, sqdiff, ccorr, ccoeff, sqdiff_normed,
        ccorr_normed, ccoeff_normed.
        """
        if value is None:
            return Settings._template_match_backend
        else:
            Settings._template_match_backend = value
    #: name of the template matching backend
    template_match_backend = property(fget=template_match_backend, fset=template_match_backend)

    def feature_detect_backend(self, value=None):
        """
        Same as :py:func:`Settings.image_logging_destination` but with

        :param value: name of the feature detection backend

        Supported  backends: BruteForce, BruteForce-L1, BruteForce-Hamming,
        BruteForce-Hamming(2), in-house-raw, in-house-region.
        """
        if value is None:
            return Settings._feature_detect_backend
        else:
            Settings._feature_detect_backend = value
    #: name of the feature detection backend
    feature_detect_backend = property(fget=feature_detect_backend, fset=feature_detect_backend)

    def feature_extract_backend(self, value=None):
        """
        Same as :py:func:`Settings.image_logging_destination` but with

        :param value: name of the feature extraction backend

        Supported backends: ORB, FAST, STAR, GFTT, HARRIS, Dense, oldSURF.
        """
        if value is None:
            return Settings._feature_extract_backend
        else:
            Settings._feature_extract_backend = value
    #: name of the feature extraction backend
    feature_extract_backend = property(fget=feature_extract_backend, fset=feature_extract_backend)

    def feature_match_backend(self, value=None):
        """
        Same as :py:func:`Settings.image_logging_destination` but with

        :param value: name of the feature matching backend

        Supported backends: ORB, BRIEF, FREAK.
        """
        if value is None:
            return Settings._feature_match_backend
        else:
            Settings._feature_match_backend = value
    #: name of the feature matching backend
    feature_match_backend = property(fget=feature_match_backend, fset=feature_match_backend)


class Settings(object):
    """
    Handler for default configuration present in all
    cases where no specific value is set.

    The methods of this class are shared among
    all of its instances.
    """
    __metaclass__ = Settings


class DCEqualizer(object):
    """
    Container for the desktop control backend configuration,
    responsible for making the backend behave according to this
    configuration as well as for providing information about it.
    """

    def __init__(self, backend=None):
        """
        Build a container for the desktop control backend configuration.

        :param backend: name of a preselected backend
        :type backend: str or None

        This class is similar to the computer vision backend configuration
        one but is simpler due to the lack of categories.

        A parameter can be accessed as follows::

            print self.p["vnc_hostname"]
        """
        self.algorithms = ("autopy", "qemu", "vncdotool")
        self.p = {}
        self._current = None

        if backend is not None:
            self.configure_backend(backend)

    def get_backend(self):
        """
        Method for compatibility with :py:class:`CVEqualizer` (however nonextended getter).

        :returns: name of the current DC backend
        :rtype: str or None
        """
        log.log(0, "desktop_control %s", self._current)
        return self._current

    def configure_backend(self, name, *args):
        """
        Change the type and parameters of a backend for the desktop control.

        :param str name: name of the new DC backend
        :param args: arguments for the new DC backend
        :type args: (str, int) or int or :py:class:`qemu_monitor.Monitor` (see Autotest)
        """
        self._current = name
        self._new_params(name)

        if name == "vncdotool":
            if len(args) == 2:
                self.p["vnc_hostname"] = args[0]
                self.p["vnc_port"] = args[1]
            elif len(args) == 1:
                self.p["vnc_port"] = args[0]
        elif name == "qemu":
            if len(args) == 1:
                self.p["qemu_monitor"] = args[0]

    def _new_params(self, new):
        """Update the parameters dictionary according to a new backend method."""
        self.p = {}
        if new == "autopy":
            # autopy has diffrent problems on different OS so specify it
            self.p["os_type"] = "linux"
        elif new == "qemu":
            # qemu monitor object in case qemu backend is used
            self.p["qemu_monitor"] = None
        elif new == "vncdotool":
            # hostname of the vnc server in case vncdotool backend is used
            self.p["vnc_hostname"] = "localhost"
            # port of the vnc server in case vncdotool backend is used
            self.p["vnc_port"] = 0
        log.log(0, "%s %s\n", new, self.p)

    def sync_backend_to_params(self, backend=None):
        """
        Synchronize the desktop control backend with the equalizer configuration.

        :param backend: preconfigured screen if any
        :type backend: :py:class:`DCScreen` or None
        :returns: new or synchronized screen
        :rtype: :py:class:`DCScreen`
        :raises: :py:class:`ValueError` if current backend is 'qemu' and no monitor is selected
        """
        if backend is None:
            backend = DCScreen()
        if self.backend == "autopy":
            import autopy
            backend.backend = autopy
            # screen size
            screen_size = backend.backend.screen.get_size()
            backend.width = screen_size[0]
            backend.height = screen_size[1]
            backend.keymap = inputmap.AutoPyKey()
            backend.modmap = inputmap.AutoPyKeyModifier()
            backend.mousemap = inputmap.AutoPyMouseButton()
        elif self.backend == "qemu":
            backend.backend = self.p["qemu_monitor"]
            if backend.backend is None:
                raise ValueError("No Qemu monitor was selected - please set a monitor object first.")
            # screen size
            with NamedTemporaryFile(prefix='guibender', suffix='.ppm') as f:
                filename = f.name
            backend.backend.screendump(filename=filename, debug=True)
            screen = PIL.Image.open(filename)
            os.unlink(filename)
            backend.width = screen.size[0]
            backend.height = screen.size[1]
            backend.keymap = inputmap.QemuKey()
            backend.modmap = inputmap.QemuKeyModifier()
            backend.mousemap = inputmap.QemuMouseButton()
        elif self.backend == "vncdotool":
            logging.getLogger('vncdotool').setLevel(logging.ERROR)
            logging.getLogger('twisted').setLevel(logging.ERROR)
            from vncdotool import api
            backend.backend = api.connect('%s:%i' % (self.p["vnc_hostname"], self.p["vnc_port"]))
            # for special characters preprocessing for the vncdotool
            backend.backend.factory.force_caps = True
            # screen size
            with NamedTemporaryFile(prefix='guibender', suffix='.png') as f:
                filename = f.name
            screen = backend.backend.captureScreen(filename)
            os.unlink(filename)
            backend.width = screen.width
            backend.height = screen.height
            backend.keymap = inputmap.VNCDoToolKey()
            backend.modmap = inputmap.VNCDoToolKeyModifier()
            backend.mousemap = inputmap.VNCDoToolMouseButton()
        return backend


class DCScreen(object):
    """A class for a synchronizable backend with the DC equalizer."""

    def __init__(self):
        """Build a desktop control screen."""
        self.backend = None
        self.pointer = (0, 0)
        self.width = 0
        self.height = 0
        self.keymap = None
        self.mousemap = None
        self.modmap = None


class CVEqualizer(object):
    """
    Container for the computer vision backend configuration,
    responsible for making the backend behave according to this
    configuration as well as for providing information about it.
    """

    def __init__(self, backend=None):
        """
        Build a container for the computer vision backend configuration.

        :param backend: name of a preselected backend
        :type backend: str or None

        Available algorithms can be seen in the `algorithms` attribute
        whose keys are the algorithm types and values are the members of
        these types.

        External (image finder) parameters:
            * detect filter - works for certain detectors and
                determines how many initial features are
                detected in an image (e.g. hessian threshold for
                SURF detector)
            * match filter - determines what part of all matches
                returned by feature matcher remain good matches
            * project filter - determines what part of the good
                matches are considered inliers
            * ratio test - boolean for whether to perform a ratio test
            * symmetry test - boolean for whether to perform a symmetry test

        .. note:: SURF and SIFT are proprietary algorithms and are not available
            by default in newer OpenCV versions (>3.0).
        .. todo:: "in-house-raw" performs regular knn matching, but "in-house-region"
            performs a special filtering and replacement of matches based on
            positional information (it does not have ratio and symmetry tests
            and assumes that the needle is transformed preserving the relative
            positions of each pair of matches, i.e. no rotation is allowed,
            but scaling for example is supported)
        """
        # currently fully compatible methods
        self.algorithms = {"find_methods": ("autopy", "template", "feature", "hybrid"),
                           "template_matchers": ("sqdiff", "ccorr",
                                                 "ccoeff", "sqdiff_normed",
                                                 "ccorr_normed", "ccoeff_normed"),
                           "feature_matchers": ("BruteForce", "BruteForce-L1", "BruteForce-Hamming",
                                                "BruteForce-Hamming(2)"),
                           "feature_detectors": ("ORB", "BRISK", "KAZE", "AKAZE", "MSER",
                                                 "AgastFeatureDetector", "FastFeatureDetector", "GFTTDetector",
                                                 "SimpleBlobDetector", "oldSURF"),
                           # TODO: we could also support "StereoSGBM" but it needs initialization arguments
                           "feature_extractors": ("ORB", "BRISK", "KAZE", "AKAZE")}

        # parameters registry
        self.p = {"find": {}, "tmatch": {}, "fextract": {}, "fmatch": {}, "fdetect": {}}

        # default algorithms
        self._current = {}
        if backend is not None:
            self.configure_backend(find_image=backend,
                                   template_match=Settings.template_match_backend,
                                   feature_detect=Settings.feature_detect_backend,
                                   feature_extract=Settings.feature_extract_backend,
                                   feature_match=Settings.feature_match_backend)

    def get_backend(self, category):
        """
        Extended getter for backend attributes.

        :param str category: supported category, see `algorithms`
        :returns: current (sub)backend for the selected category
        :rtype: str
        """
        full_names = {"find": "find_methods",
                      "tmatch": "template_matchers",
                      "fdetect": "feature_detectors",
                      "fextract": "feature_extractors",
                      "fmatch": "feature_matchers"}
        log.log(0, "%s %s", category, self._current[category])
        return self.algorithms[full_names[category]][self._current[category]]

    def set_backend(self, category, value):
        """
        Extended setter for backend attributes.

        :param str category: supported category, see `algorithms`
        :param str value: supported category backend, see `algorithms[category]`
        :raises: :py:class:`ImageFinderMethodError` if `value` is not among the
                 supported category backends
        """
        full_names = {"find": "find_methods",
                      "tmatch": "template_matchers",
                      "fdetect": "feature_detectors",
                      "fextract": "feature_extractors",
                      "fmatch": "feature_matchers"}
        if value not in self.algorithms[full_names[category]]:
            raise ImageFinderMethodError
        else:
            self._new_params(category, value)
            self._current[category] = self.algorithms[full_names[category]].index(value)

    def configure_backend(self, find_image=None, template_match=None,
                          feature_detect=None, feature_extract=None,
                          feature_match=None):
        """
        Change some or all of the algorithms used as backend for the image finder.

        All parameters are strings supported in `algorithms` or None (no change).
        """
        if find_image != None:
            log.log(0, "Setting main backend to %s", find_image)
            self.set_backend("find", find_image)
        if template_match != None:
            log.log(0, "Setting backend for template matching to %s", template_match)
            self.set_backend("tmatch", template_match)
        if feature_detect != None:
            log.log(0, "Setting backend for feature detection to %s", feature_detect)
            self.set_backend("fdetect", feature_detect)
        if feature_extract != None:
            log.log(0, "Setting backend for feature extraction to %s", feature_extract)
            self.set_backend("fextract", feature_extract)
        if feature_match != None:
            log.log(0, "Setting backend for feature matching to %s", feature_match)
            self.set_backend("fmatch", feature_match)

    def _new_params(self, category, new):
        """Update the parameters dictionary according to a new backend algorithm."""
        self.p[category] = {}
        if category == "find":
            self.p[category]["similarity"] = CVParameter(0.9, 0.0, 1.0, 0.1, 0.1)
            if new in ("feature", "hybrid"):
                self.p[category]["ransacReprojThreshold"] = CVParameter(0.0, 0.0, 200.0, 10.0, 1.0)
            if new in ("template", "hybrid"):
                self.p[category]["nocolor"] = CVParameter(False)
            if new == "hybrid":
                self.p[category]["front_similarity"] = CVParameter(0.8, 0.0, 1.0, 0.1, 0.1)
            # although it is currently not available
            elif new == "2to1hybrid":
                self.p[category]["x"] = CVParameter(1000, 1, None)
                self.p[category]["y"] = CVParameter(1000, 1, None)
                self.p[category]["dx"] = CVParameter(100, 1, None)
                self.p[category]["dy"] = CVParameter(100, 1, None)
            return
        elif category == "tmatch":
            return
        elif category == "fdetect":
            self.p[category]["nzoom"] = CVParameter(4.0, 1.0, 10.0, 1.0, 1.0)
            self.p[category]["hzoom"] = CVParameter(4.0, 1.0, 10.0, 1.0, 1.0)

            if new == "oldSURF":
                self.p[category]["oldSURFdetect"] = CVParameter(85)
                return
            else:
                feature_detector_create = getattr(cv2, "%s_create" % new)
                new_backend = feature_detector_create()

        elif category == "fextract":
            descriptor_extractor_create = getattr(cv2, "%s_create" % new)
            new_backend = descriptor_extractor_create()
        elif category == "fmatch":
            if new == "in-house-region":
                self.p[category]["refinements"] = CVParameter(50, 1, None)
                self.p[category]["recalc_interval"] = CVParameter(10, 1, None)
                self.p[category]["variants_k"] = CVParameter(100, 1, None)
                self.p[category]["variants_ratio"] = CVParameter(0.33, 0.0001, 1.0)
                return
            else:
                self.p[category]["ratioThreshold"] = CVParameter(0.65, 0.0, 1.0, 0.1)
                self.p[category]["ratioTest"] = CVParameter(False)
                self.p[category]["symmetryTest"] = CVParameter(False)

                # no other parameters are used for the in-house-raw matching
                if new == "in-house-raw":
                    return
                else:

                    # BUG: a bug of OpenCV leads to crash if parameters
                    # are extracted from the matcher interface although
                    # the API supports it - skip fmatch for now
                    return

                    # NOTE: descriptor matcher creation is kept the old way while feature
                    # detection and extraction not - example of the untidy maintenance of OpenCV
                    new_backend = cv2.DescriptorMatcher_create(new)

        # examine the interface of the OpenCV backend
        log.log(0, "%s %s", new_backend, dir(new_backend))
        for attribute in dir(new_backend):
            if not attribute.startswith("get"):
                continue
            param = attribute.replace("get", "")
            get_param = getattr(new_backend, attribute)
            val = get_param()
            if type(val) not in [bool, int, float, type(None)]:
                continue

            # give more information about some better known parameters
            if category in ("fdetect", "fextract") and param == "firstLevel":
                self.p[category][param] = CVParameter(val, 0, 100)
            elif category in ("fdetect", "fextract") and param == "nFeatures":
                self.p[category][param] = CVParameter(val, delta=100)
            elif category in ("fdetect", "fextract") and param == "WTA_K":
                self.p[category][param] = CVParameter(val, 2, 4)
            elif category in ("fdetect", "fextract") and param == "scaleFactor":
                self.p[category][param] = CVParameter(val, 1.01, 2.0)
            else:
                self.p[category][param] = CVParameter(val)
            log.debug("%s=%s", param, val)

        log.log(0, "%s %s\n", category, self.p[category])
        return

    def sync_backend_to_params(self, backend, category):
        """
        Synchronize the computer vision backend with the equalizer configuration.

        :param backend: supported category backend, see `algorithms[category]`
        :type backend: external backend class depending on the category backend choice
        :param str category: supported category, see `algorithms`
        :returns: synchronized category backend
        :rtype: external backend class depending on the category backend choice

        In particular, synchronize the inner OpenCV parameters of detectors,
        extractors, and matchers with the equalizer configuration.
        """
        if (category == "find" or category == "tmatch" or
                (category == "fdetect" and self.get_backend(category) == "oldSURF")):
            return backend
        elif category == "fmatch":
            # no internal OpenCV parameters to sync with
            if self.get_backend(category) in ("in-house-raw", "in-house-region"):
                return backend

            # BUG: a bug of OpenCV leads to crash if parameters
            # are extracted from the matcher interface although
            # the API supports it - skip fmatch for now
            else:
                return backend

        for attribute in dir(backend):
            if not attribute.startswith("get"):
                continue
            param = attribute.replace("get", "")
            if param in self.p[category]:
                val = self.p[category][param].value
                set_attribute = attribute.replace("get", "set")
                # some getters might not have corresponding setters
                if not hasattr(backend, set_attribute):
                    continue
                set_param = getattr(backend, set_attribute)
                set_param(val)
                log.log(0, "Synced %s to %s", param, val)
                self.p[category][param].value = val
        return backend

    def can_calibrate(self, mark, category):
        """
        Fix the parameters for a given category backend algorithm,
        i.e. disallow the calibrator to change them.

        :param bool mark: whether to mark for calibration
        :param str category: backend category whose parameters are marked
        :raises: :py:class:`ImageFinderMethodError` if `category` is not among the
                 supported backend categories
        """
        if category not in self.p:
            raise ImageFinderMethodError

        for param in self.p[category].values():
            # BUG: force fix parameters that have internal bugs
            if category == "fextract" and param == "bytes":
                param.fixed = True
            else:
                param.fixed = not mark

    def from_match_file(self, filename_without_extention):
        """
        Read the configuration from a .match file with the given filename.

        :param str filename_without_extention: match filename for the configuration
        :raises: :py:class:`IOError` if the respective match file couldn't be read
        """
        parser = config.RawConfigParser()
        # preserve case sensitivity
        parser.optionxform = str

        success = parser.read("%s.match" % filename_without_extention)
        # if no file is found throw an exception
        if len(success) == 0:
            raise IOError

        for category in self.p.keys():
            if parser.has_section(category):
                section_backend = parser.get(category, 'backend')
                if section_backend != self.get_backend(category):
                    self.set_backend(category, section_backend)
                for option in parser.options(category):
                    if option == "backend":
                        continue
                    param_string = parser.get(category, option)
                    param = CVParameter.from_string(param_string)
                    log.log(0, "%s %s", param_string, param)
                    self.p[category][option] = param

        # except (config.NoSectionError, config.NoOptionError, ValueError) as ex:
        #    print("Could not read config file '%s': %s." % (filename, ex))
        #    print("Please change or remove the config file.")

    def to_match_file(self, filename_without_extention):
        """
        Write the configuration in a .match file with the given filename.

        :param str filename_without_extention: match filename for the configuration
        """
        parser = config.RawConfigParser()
        # preserve case sensitivity
        parser.optionxform = str

        sections = self.p.keys()
        for section in sections:
            if not parser.has_section(section):
                parser.add_section(section)
            parser.set(section, 'backend', self.get_backend(section))
            for option in self.p[section]:
                log.log(0, "%s %s", section, option)
                parser.set(section, option, self.p[section][option])

        with open("%s.match" % filename_without_extention, 'w') as configfile:
            configfile.write("# IMAGE MATCH DATA\n")
            parser.write(configfile)


class CVParameter(object):
    """A class for a single parameter from the CV equalizer."""

    def __init__(self, value,
                 min_val=None, max_val=None,
                 delta=1.0, tolerance=0.1,
                 fixed=True):
        """
        Build a computer vision parameter.

        :param value: value of the parameter
        :type value: bool or int or float or None
        :param min_val: lower boundary for the parameter range
        :type min_val: int or float or None
        :param max_val: upper boundary for the parameter range
        :type max_val: int or float or None
        :param float delta: delta for the calibration
                            (no calibration if `delta` < `tolerance`)
        :param float tolerance: tolerance of calibration
        :param bool fixed: whether the parameter is prevented from calibration
        """
        self.value = value
        self.delta = delta
        self.tolerance = tolerance

        # force specific tolerance and delta for bool and
        # int parameters
        if type(value) == bool:
            self.delta = 0.0
            self.tolerance = 1.0
        elif type(value) == int:
            self.delta = 1
            self.tolerance = 0.9

        if min_val != None:
            assert value >= min_val
        if max_val != None:
            assert value <= max_val
        self.range = (min_val, max_val)

        self.fixed = fixed

    def __repr__(self):
        """
        Provide a representation of the parameter for storing and reporting.

        :returns: special syntax representation of the parameter
        :rtype: str
        """
        return ("<value='%s' min='%s' max='%s' delta='%s' tolerance='%s' fixed='%s'>"
                % (self.value, self.range[0], self.range[1], self.delta, self.tolerance, self.fixed))

    @staticmethod
    def from_string(raw):
        """
        Parse a CV parameter from string.

        :param str raw: string representation for the parameter
        :returns: parameter parsed from the representation
        :rtype: :py:class:`CVParameter`
        :raises: :py:class:`ValueError` if unsupported type is encountered
        """
        args = []
        string_args = re.match(r"<value='(.+)' min='([\d.None]+)' max='([\d.None]+)'"
                               r" delta='([\d.]+)' tolerance='([\d.]+)' fixed='(\w+)'>",
                               raw).group(1, 2, 3, 4, 5, 6)
        for arg in string_args:
            if arg == "None":
                arg = None
            elif arg == "True":
                arg = True
            elif arg == "False":
                arg = False
            elif re.match(r"\d+$", arg):
                arg = int(arg)
            elif re.match(r"[\d.]+", arg):
                arg = float(arg)
            else:
                raise ValueError

            log.log(0, "%s %s", arg, type(arg))
            args.append(arg)

        log.log(0, "%s", args)
        return CVParameter(*args)
