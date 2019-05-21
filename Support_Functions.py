#!/tool/pandora64/bin/python3

"""
Generic support functions that could likely come from a different library.
"""
import shlex
import subprocess
import logging
import os
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import xml.etree.ElementTree as ET


def execute_command(cmd='echo hello'):
    """
    Execute a command in sub-process.

    Refer to - https://stackoverflow.com/questions/4760215/running-shell-command-and-capturing-the-output

    Parameters
    ----------
    cmd : str
        command to execute

    Returns
    -------
    std_out : str
        Standard output of the executed command
    std_err : str
        Standard error of the executed command
    return_code : str
        Sub-process returned error code
    """
    proc = subprocess.run(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out = proc.stdout.decode('utf-8')
    std_err = proc.stderr.decode('utf-8')
    return_code = str(proc.returncode)

    return std_out, std_err, return_code


def log_config():
    """
    Configure the log file output.  It's that simple.
    """

    # Royal pain in the neck to figure out this was required.
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(module)-20s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='kw_update_log.txt',
                        filemode='w',
                        )
    logging.info("Log File is initialized.")


def cmd_args_parse(args=sys.argv[1:]):
    """
    Shocker here, this will parse the list provided for command line arguments.

    Parameters
    ----------
    args : list
        The list of strings, which should probably always be the default of sys.argv[1:]

    Returns
    -------
        The command line arguments to be applied.
    """

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('-j', '--job_file', action="store", dest="job_file", type=str, required=True,
                        help='Use this option to define the base job file.')

    parser.add_argument('-u', '--update', action="store_true", dest="update_job_file", default=False,
                        help='Update the Job File to be DB-Based and use standard generics.')

    parser.add_argument('-p', '--preserve_job_file', action="store_true", dest="preserve_job_file", default=False,
                        help='Keep a copy of the original job file that is pulled.')

    parser.add_argument('-r', '--run_setup', action="store_true", dest="run_setup", default=False,
                        help='Run the Job Setup Command.')

    parser.add_argument('-v', '--verbose', action="store_true", dest="verbose",
                        help='Enable log output.', default=False)

    # This is needed to remove keys where the value is None
    args_output = {}
    for key, value in vars(parser.parse_args(args)).items():
        if value is not None:
            args_output[key] = value
        else:
            logging.info("Removing the unused command line arg %s", key)

    return args_output


def get_stack_list(level_family, stack_opt):
    """
    Based on a bla bla bla
        return a list containing the sequence of bla bla bla.

    Parameters
    ----------
    level_family :str
        The level fam as per specs locked in _____
    stack_opt : str
        Yeah, ommm, I think this is clear.

    Returns
    -------
    list - containing some stuff that's in sequence.

    """
    stack_def = {
        "BLA": {
         'OPT1':  ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
		 'OPT2':  ['A', 'C', 'D', 'E', 'F', 'G'],
		 'OPT3':  ['A', 'B', 'C', 'E', 'F', 'G']
        }
    }

    if level_family not in stack_def:
        logging.error("The bla bla bla %s", level_family)
        return None

    if stack_opt not in stack_def[level_family]:
        logging.error("The bla bla %s bla %s", stack_opt, level_family)
        return None

    return stack_def[level_family][stack_opt]


def get_level_info(level_family):
    """
    I can explain

    Parameters
    ----------
    ltn : str
        The level family

    Returns
    -------
    dict - if the XML file for the level family is found.  None if there is an error.
    """
    level_definition_xml_file = "/some/standard/path/" + level_family + "/Released/" + level_family + ".xml"

    if not os.path.exists(level_definition_xml_file):
        logging.error("The level definition file for %s wasn't found.", level_definition_xml_file)
        return None

    tree = ET.parse(level_definition_xml_file)
    root = tree.getroot()

    layer_config_info = {}

    for level in root.findall("./Level"):
        # There could be considerable error handling added here
        #   But considering the source, I'm skeptical of the value add
        level_name = layer.get("name", "")
        level_aspect_one = layer.find("aspect_one").text
		level_aspect_two = layer.find("aspect_two").text
		level_aspect_three = layer.find("aspect_three").text
        level_config_info[level_name] = {"Bla1": level_aspect_one, "bla2": level_aspect_two, "bla3": level_aspect_three}

    return level_config_info