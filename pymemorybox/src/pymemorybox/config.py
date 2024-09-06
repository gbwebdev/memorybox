import toml
import enum
import datetime
from os import path
from peripage import PrinterType

import re
from flask import current_app, g

class MemoriesSourceType(enum.Enum):
    LOCAL = 'Local Path'
    REPOSITORY = 'Repository'

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Config(metaclass=Singleton):
    """Application's end-user configuration (that can be changed through the UI)
    """

    mac_regexp = re.compile('^[0-9a-f]{2}(?::[0-9a-f]{2}){5}$', re.IGNORECASE)
    time_regexp = re.compile('^[0:2][0-9]:[0:5][0-9]$')
    def __init__(self):
        self._conf_path = path.join(current_app.instance_path, 'config.toml')
        self._autosave = False

        self._memories_source_type = MemoriesSourceType.LOCAL
        self._memories_local_path = None
        self._memories_repository = None
        self._memories_repository_ignore_certificate = False
        self._enable_printing = False
        self._enable_daily_printing = False
        self._workday_print_time = datetime.time(hour=8, minute=0)
        self._holiday_print_time = datetime.time(hour=9, minute=30)
        self._enable_holiday_mode = False
        self._printer_mac_address = "01:23:45:67:89:AF"
        self._printer_model = PrinterType.A6p
        self._printer_concentration = 1
        self._optimize_orientation = True
        self._print_captation = True

        self.load_conf()

    def save_conf(self):
        """Save configuration to configuration file
        """
        config_data = {
            'picture_source': {
                'source_type': self._memories_source_type.name,
                'local': {
                    'path': self._memories_local_path
                },
                'repository': {
                    'address': self._memories_repository,
                    'ignore_certificate': self._memories_repository_ignore_certificate
                }
            },
            'printing':{
                'enabled': self._enable_printing,
                'settings': {
                    'printer_mac_address': self._printer_mac_address,
                    'printer_model': self._printer_model.name,
                    'printer_concentration': self._printer_concentration,
                    'optimize_orientation': self._optimize_orientation,
                    'print_captation': self._print_captation,
                    'daily_printing': {
                        'enabled': self._enable_daily_printing,
                        'settings': {
                            'workday_print_time': self._workday_print_time.strftime('%H:%M'),
                            'holiday_print_time': self._holiday_print_time.strftime('%H:%M'),
                            'holiday_mode_enabled': self._enable_holiday_mode
                        }
                    }
                }
            }
        }
        
        with open(self._conf_path, 'w', encoding='utf-8') as config_file:
            toml.dump(config_data, config_file)

    def load_conf(self):
        """Load configuration from configuration file
        """
        try :
            config_data = toml.load(self._conf_path)

            picture_source = config_data.get('picture_source', {})
            self._memories_source_type = \
                MemoriesSourceType[picture_source.get('source_type', self._memories_source_type.name)]
            self._memories_local_path = picture_source.get('local', {}) \
                                            .get('path', self._memories_local_path)
            self._memories_repository = picture_source.get('repository', {}) \
                                            .get('address', self._memories_repository)
            self._memories_repository_ignore_certificate = picture_source.get('repository', {}) \
                                            .get('ignore_certificate',
                                                self._memories_repository_ignore_certificate)
            
            printing = config_data.get('printing', {})
            self._enable_printing = printing.get('enabled', self._enable_printing)
            printing_settings = printing.get('settings', {})
            self._printer_mac_address = printing_settings.get('printer_mac_address',
                                                              self._printer_mac_address)
            self._printer_model = PrinterType[printing_settings.get('printer_model',
                                                                    self._printer_model.name)]
            self._printer_concentration = printing_settings.get('printer_concentration',
                                                                    self._printer_concentration)
            self._optimize_orientation = printing_settings.get('optimize_orientation',
                                                               self._optimize_orientation)
            self._print_captation = printing_settings.get('print_captation',
                                                               self._print_captation)

            daily_printing = printing_settings.get('daily_printing', {})
            self._enable_daily_printing = daily_printing.get('enabled', self._enable_daily_printing)
            daily_printing_settings = printing_settings.get('settings', {})
            self._workday_print_time = datetime.datetime.strptime(
                    daily_printing_settings.get('workday_print_time',
                                                self._workday_print_time.strftime('%H:%M')),
                    "%H:%M"
                ).time()
            self._holiday_print_time = datetime.datetime.strptime(
                    daily_printing_settings.get('holiday_print_time',
                                                self._holiday_print_time.strftime('%H:%M')),
                    "%H:%M"
                ).time()
            self._enable_holiday_mode = daily_printing_settings.get('holiday_mode_enabled',
                                                                    self._enable_holiday_mode)
        except FileNotFoundError:
            print("Config file does not exist yet.")

    def _handle_autosave(self):
        if self._autosave:
            self.save_conf()

    @property
    def autosave(self) -> bool:
        """If True, the configuration will be automatically saved everytime a setting changes.
        """
        return self._autosave

    @autosave.setter
    def autosave(self, autosave: bool):
        self._autosave = autosave

    @property
    def memories_source_type(self) -> MemoriesSourceType:
        """Type of source for the memories packages.
        """
        return self._memories_source_type

    @memories_source_type.setter
    def memories_source_type(self, memories_source_type: MemoriesSourceType):
        self._memories_source_type = memories_source_type
        self._handle_autosave()

    @property
    def memories_local_path(self) -> path:
        """Path of the local directory for the memories packages.
        """
        return self._memories_local_path

    @memories_local_path.setter
    def memories_local_path(self, memories_local_path: path):
        self._memories_local_path = memories_local_path
        self._handle_autosave()

    @property
    def memories_repository(self) -> str:
        """Address of the repository server for the memories packages.
        """
        return self._memories_repository

    @memories_repository.setter
    def memories_repository(self, memories_repository: str):
        self._memories_repository = memories_repository
        self._handle_autosave()

    @property
    def memories_repository_ignore_certificate(self) -> bool:
        """Ignore certificate when connecting to the repository server for the memories packages.
        """
        return self._memories_repository_ignore_certificate

    @memories_repository_ignore_certificate.setter
    def memories_repository_ignore_certificate(self, memories_repository_ignore_certificate: bool):
        self._memories_repository_ignore_certificate = memories_repository_ignore_certificate
        self._handle_autosave()

    @property
    def enable_printing(self) -> bool:
        """Enable printing.
        """
        return self._enable_printing

    @enable_printing.setter
    def enable_printing(self, enable_printing: bool):
        self._enable_printing = enable_printing
        self._handle_autosave()

    @property
    def enable_daily_printing(self) -> bool:
        """Enable automatic printing of the day's memory.
        """
        return self._enable_daily_printing

    @enable_daily_printing.setter
    def enable_daily_printing(self, enable_daily_printing: bool):
        self._enable_daily_printing = enable_daily_printing
        self._handle_autosave()

    @property
    def workday_print_time(self) -> datetime.time:
        """Time at which the daily memory should be printed on a workday.
        """
        return self._workday_print_time

    @workday_print_time.setter
    def workday_print_time(self, workday_print_time: datetime.time):
        self._workday_print_time = workday_print_time
        self._handle_autosave()

    @property
    def holiday_print_time(self) -> datetime.time:
        """Time at which the daily memory should be printed on a weekend / holiday.
        """
        return self._holiday_print_time

    @holiday_print_time.setter
    def holiday_print_time(self, holiday_print_time: datetime.time):
        self._holiday_print_time = holiday_print_time
        self._handle_autosave()

    @property
    def enable_holiday_mode(self) -> bool:
        """Enable holiday mode (when enabled, everyday is considered a holiday).
        """
        return self._enable_holiday_mode

    @enable_holiday_mode.setter
    def enable_holiday_mode(self, enable_holiday_mode: bool):
        self._enable_holiday_mode = enable_holiday_mode
        self._handle_autosave()

    @property
    def printer_mac_address(self) -> str:
        """MAC address of the printer.
        """
        return self._printer_mac_address

    @printer_mac_address.setter
    def printer_mac_address(self, printer_mac_address: str):
        assert Config.mac_regexp.match(printer_mac_address)
        self._printer_mac_address = printer_mac_address
        self._handle_autosave()

    @property
    def printer_concentration(self) -> int:
        """Printing concentration.
        """
        return self._printer_concentration

    @printer_concentration.setter
    def printer_concentration(self, printer_concentration: int):
        self._printer_concentration = printer_concentration
        self._handle_autosave()

    @property
    def printer_model(self) -> PrinterType:
        """Model of the printer.
        """
        return self._printer_model

    @printer_model.setter
    def printer_model(self, printer_model: PrinterType):
        self._printer_model = printer_model
        self._handle_autosave()

    @property
    def optimize_orientation(self) -> bool:
        """Optimize image orientation (rotate if picture is wider than height).
        """
        return self._optimize_orientation

    @optimize_orientation.setter
    def optimize_orientation(self, optimize_orientation: bool):
        self._optimize_orientation = optimize_orientation
        self._handle_autosave()

    @property
    def print_captation(self) -> bool:
        """Print the captation with the picture.
        """
        return self._print_captation

    @print_captation.setter
    def print_captation(self, print_captation: bool):
        self._print_captation = print_captation
        self._handle_autosave()
