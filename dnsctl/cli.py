import os
import sys
from ipaddress import IPv4Address, IPv4Network
from pathlib import Path

import dynaconf
import rich_click as click
from jinja2 import Environment, FileSystemLoader, PackageLoader
from loguru import logger

from dnsctl.config import settings

click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
logger.remove()

format_logger = '<green>{time}</green> | <level>{level}</level> | <blue>{name}:{function}:{line}</blue> - <level>{message}</level>'

@click.group('cli')
@click.option(
    '--log',
    type=str,
    help='Log Level, Default: INFO',
    required=True,
    default='DEBUG',
)
def cli(log):
    """
    # dnschanger
    ### Exemplos:
    - $ dnsctl failover --link LINK
    - $ dnsctl view --link LINK
    """
    logger.add(
        sys.stdout,
        level=log.upper(),
        colorize=True,
        format=format_logger,
    )

    logger.add(
        'dnschanger.log',
        rotation='10 KB',
        level=log.upper(),
        format=format_logger,
    )

@cli.command('version', help='Version tool')
def version():
    click.echo('dnsctl 0.1.1')


@cli.command('view', short_help='View DNS records')
@click.option(
    '--link',
    '-l',
    '-L',
    type=str,
    help='Nome do link',
    required=True,
    default='ALL',
)
def view(link):
    """
    Visualiza previamente os dados
    """
    ...

@cli.command('failover', short_help='failover DNS records')
@click.option(
    '--link', '-l', '-L', type=str, help='Nome do link', required=True
)
def failover(link):
    """
    Ex:
    - $ dnsctl failover --link LINK ./domain.yml
    """
    path_dir = './dnsctl/templates'
    named_file = Path(settings.named_file)

    loader = FileSystemLoader(searchpath=path_dir)
    env = Environment(loader=loader, autoescape=True)
    default_template = env.get_template('base.j2')
    template_records = env.get_template('records.j2')
    buf = default_template.render(domain=settings.domain)
    get_cidr_info = [
        cidr for cidr in settings.cidr if link.upper() in cidr.name
    ]
    cidr = get_cidr_info[0].addr
    records = settings.records
    domain = settings.domain

    with named_file.open('w') as fp:
        fp.write(buf)

    for record in records:
        match record:
            case {'mode': 'failover', 'type': 'A'}:
                if type(record['addr']) is not str:
                    address = [
                        ipaddr
                        for ipaddr in record['addr']
                        if IPv4Address(ipaddr) in IPv4Network(cidr)
                    ]
                    record_template = template_records.render(
                        display_info=settings.display_info,
                        info=record['info'],
                        mode=record['mode'],
                        name=record['name'],
                        type=record['type'],
                        ip=address[0],
                    )
                    logger.debug(
                        f'domain: {settings.domain} : {record_template}'
                    )
                    with named_file.open('a') as f:
                        f.write(f'{record_template}\n')
                else:
                    logger.error(
                        f"Altere o mode para standalone  [ domain: {settings.domain} name: {record['name']}, mode: {record['mode']} ] "
                    )

            case {'mode': 'roundrobin', 'type': 'A'}:
                if type(record['addr']) is not str:
                    for ip in record['addr']:
                        record_template = template_records.render(
                            display_info=settings.display_info,
                            mode=record['mode'],
                            name=record['name'],
                            type=record['type'],
                            info=record['info'],
                            ip=ip,
                        )
                        logger.debug(f'domain: {settings.domain} : {record_template}')
                        with named_file.open('a') as f:
                            f.write(f'{record_template}\n')
                else:
                    logger.error(
                        f"Altere o mode para standalone  [ name: {record['name']}, mode: {record['mode']} ] "
                    )

            case {'mode': 'standalone', 'type': 'A'}:
                if type(record['addr']) is str:
                    record_template = template_records.render(
                        display_info=settings.display_info,
                        info=record['info'],
                        mode=record['mode'],
                        name=record['name'],
                        type=record['type'],
                        ip=record['addr'],
                    )
                    logger.debug(f'domain: {settings.domain} : {record_template}')
                    with named_file.open('a') as f:
                        f.write(f'{record_template}\n')
                else:
                    logger.error(
                        f"Altere o mode para failover ou roundrobin [ name: {record['name']}, mode: {record['mode']} ] "
                    )
            case {'type': 'CNAME'}:
                if type(record['addr']) is str:
                    record_template = template_records.render(
                        display_info=settings.display_info,
                        info=record['info'],
                        name=record['name'],
                        type=record['type'],
                        ip=record['addr'],
                    )
                    logger.debug(f'domain: {settings.domain} : {record_template}')
                    with named_file.open('a') as f:
                        f.write(f'{record_template}\n')
                else:
                    logger.error(
                        f"Altere o mode para failover ou roundrobin [ name: {record['name']} ]"
                    )


@cli.command('install', short_help='Instala o dnsctl')
@click.option(
    '--user',
    'install',
    flag_value='user',
    help='Instala no usuário ou no sistema',
)
@click.option(
    '--system',
    'install',
    flag_value='system',
    help='Instala no usuário ou no sistema',
)
# @click.option('--system', is_flag=True, help='Nome do link')
def install(install):
    if install == 'user':
        log_path = Path.home().joinpath('.local/share/dnsctl/log')
        config_path = Path.home().joinpath('.config/dnsctl')
        log_path.mkdir(parents=True, exist_ok=True)
        config_path.mkdir(parents=True, exist_ok=True)
        logger.info(f' Diretorio dos logs: {log_path}')
        logger.info(f' Diretorio das configuração: {config_path}')
        click.echo(type(settings.system.log.upper()))
    else:
        path = Path('/etc')
        click.echo(path)
        # click.echo(dir(settings))
        # click.echo(settings.root_path_for_dynaconf)
        click.echo(settings.cidr)
        click.echo(settings.domain)
