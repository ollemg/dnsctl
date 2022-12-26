import rich_click as click
from loguru import logger
from pathlib import Path
import sys
import dynaconf
from ipaddress import IPv4Network, IPv4Address
from dnsctl.config import settings
import os
from jinja2 import PackageLoader, Environment, FileSystemLoader

click.rich_click.USE_MARKDOWN = True
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True
# click.rich_click.ERRORS_SUGGESTION = "Try running the '--help' flag for more information."
logger.remove()

format_logger = '<green>{time}</green> | <level>{level}</level> | <blue>{name}:{function}:{line}</blue> - <level>{message}</level>'
# format_stderr = '<level>{level}</level> - <level>{message}</level>'


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
    ## Exemplos:
    - $ dnsctl failover --link LINK ./domain.yml
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
    click.echo('dnschanger 0.5.0')


@cli.command('view', short_help='View DNS records')
@click.argument('dns_yml_config', type=click.Path(exists=True, readable=True))
@click.option(
    '--link',
    '-l',
    '-L',
    type=str,
    help='Nome do link',
    required=True,
    default='ALL',
)
def view(dns_yml_config, link):
    """
    Visualiza previamente os dados
    """
    records = read_yaml(dns_yml_config, 'records')
    domain = read_yaml(dns_yml_config, 'domain')
    named_filename = read_yaml(dns_yml_config, 'named_file')


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
    # click.echo(settings.cidr)
    # click.echo(get_cidr_info)
    cidr = get_cidr_info[0].addr
    records = settings.records
    domain = settings.domain

    with named_file.open('w') as fp:
        fp.write(buf)

    for record in records:
        # click.echo(type(record['addr']))
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
                    logger.debug(f'domain: {settings.domain} : {record_template}')
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
                        logger.debug(record_template)
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
                    logger.debug(record_template)
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
                    logger.debug(record_template)
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
