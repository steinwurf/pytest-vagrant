import csv
import re

from . import parse_format
from . import machine_status
from . import ssh_config


def to_status(output):
    """ Parse the output of 'vagrant status --machine-readable' """

    for row in csv.reader(output.splitlines()):

        if row[parse_format.ParseFormat.TYPE] != 'state':
            continue

        status = row[parse_format.ParseFormat.DATA]
        return machine_status.MachineStatus(status=status)

    raise RuntimeError("Parsing state failed")


def to_snapshot_list(output):
    """ Parse the output of 'vagrant snapshot list --machine-readable' """
    snapshots = []

    for row in csv.reader(output.splitlines()):

        if row[parse_format.ParseFormat.DATA] not in ["detail", "output"]:
            continue

        # if the is a space in the extra data we don't have a valid
        # snapshot
        if " " in row[parse_format.ParseFormat.EXTRA]:
            continue

        snapshots.append(row[parse_format.ParseFormat.EXTRA])

    return snapshots


def to_ssh_config(output):
    """ Parse the output of 'vagrant ssh-config' """

    hostname = re.search(r'HostName (.*)', output).group(1)
    username = re.search(r'User (.*)', output).group(1)
    port = int(re.search(r'Port (.*)', output).group(1))
    identityfile = re.search(r'IdentityFile (.*)', output).group(1)

    return ssh_config.SSHConfig(
        hostname=hostname, username=username, port=port,
        identityfile=identityfile)
