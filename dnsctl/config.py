from pathlib import Path
from dynaconf import Dynaconf
from glob import glob

yaml = glob('/home/ollemg/.config/dnsctl/*.yml')
config_path = Path.home().joinpath('.config/dnsctl')

settings = Dynaconf(
    envvar_prefix='DNSCHANCER',
    root_path=config_path,
    settings_files=[
        'config.toml',
    ],
    includes=yaml
)
