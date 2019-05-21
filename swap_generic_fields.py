#!/tool/pandora64/bin/python3

"""
Swap generic fields into a script file prior to execution.
"""

import os
import logging
import re
import support_functions

# The command line args will be a global variable
cmd_args = {}


def define_swap_dictionary():
    """
    This function returns a dictionary of what to replace in the job file.
    """
    sub_dictionary = {
        "%SWAP_STARK%": get_value("NORTHERN"),
        "%SWAP_LANNISTER%": get_value("GOLD"),
        "%SWAP_TARGARYEN%": get_value("DRAGON"),
        "%SWAP_BARATHEON%": get_value("BIG_AXE_MAKE_BOOM"),
        "%SWAP_MARTELL%": get_value("CAPTAIN_COOL"),
    }

    return sub_dictionary


def define_legacy_dictionary():
    """
    This function returns a dictionary legacy generics and what to update them to.
    """
    leg_sub_dictionary = {
        "%ROBB%":    "%SWAP_STARK%",
        "%ARYA%":    "%SWAP_STARK%",
		"%EDDARD%":  "%SWAP_STARK%",
		"%SANSA%":   "%SWAP_STARK%",
        "%TYWIN%":   "%SWAP_LANNISTER%",
        "%JAMIE%":   "%SWAP_LANNISTER%",
		"%GENDRY%":  "%SWAP_BARATHEON%",
		"%OBERYN%":  "%SWAP_MARTELL%"
    }

    return leg_sub_dictionary


def get_value(var_name, value_override=None):
    """
    The deal here is that getting a value could come from a default Environment Variable ~or~ a command line override.

    Parameters
    ----------
    var_name : str
        The variable being sought out
    value_override : dict
        This will be command line values if not defined.  Otherwise it's a dictionary to use in place
        of the command line overrides

    Returns
    -------
        The value or None along with a warning message if it isn't found

    """
    if not value_override:
        value_override = cmd_args

    if var_name in value_override:
        value = value_override[var_name]
        logging.warning("Using Command Line Override for - %s which is %s", var_name, value)
        return value
    elif os.environ.get(var_name):
        value = os.environ[var_name]
        logging.info("Using the Env Var for %s which is %s", var_name, value)
        return value
    else:
        logging.warning("Wasn't able to assign a value for %s", var_name)
        return None


if __name__ == "__main__":

    cmd_args = support_funtions.cmd_args_parse()

    # If verbose output is requested, set the log file as such.
    if cmd_args['verbose']:
        support_funtions.log_config()

    # Set the Job file to be worked with.
    logging.info("The base job file is - %s.", cmd_args["job_file"])
    job_file = cmd_args["job_file"]

    # Configure information related to levels
    level = get_value("LEVEL")
	level_family = get_value("LEVEL_FAMILY")
    stack = support_funtions.get_stack_list(level_family, get_value("STACK"))
    level_definitions = support_funtions.get_level_info(level_family)

    level_above = stack[stack.index(level) + 1]
    level_below = stack[stack.index(level) - 1]
    logging.info("The level is %s with %s above and %s below.", level, level_above, level_below)

    # Define a dictionary where the 'key' is what will be replaced w/ the
    #  environment variable in the value.
    substitution_dictionary = define_swap_dictionary()

    # Layer UP can easily be expanded -
    substitution_dictionary["%SWAP_LEVEL_UP%"] = level_definitions[level_above]["INFO"]

    # Read the content of the Job File to a String.
    with open(job_file, "rt") as file_in:
        job_file_content = file_in.read()

    # Scan for any possible generics to be swapped.
    #  Update legacy generics if there are any.
    #  Warn folks if needed.
    legacy_generics = define_legacy_dictionary()
    possible_generics = re.findall(r'%\S+?%', job_file_content)
    if possible_generics is None:
        logging.info("There weren't any possible generics found in the script file.  Strange.")
    else:
        for generic in sorted(set(possible_generics)):
            if generic in substitution_dictionary:
                logging.info("%s found in job file which is supported.", generic)
            elif generic in legacy_generics:
                logging.info("%s found in job file which will be updated to %s", generic, legacy_generics[generic])
                job_file_content = job_file_content.replace(generic, legacy_generics[generic])
            else:
                logging.warning("%s in job file but not a current or legacy configured generic", generic)

    if cmd_args["update_job_file"]:
        with open(job_file + "_updated", "wt") as file_out:
            file_out.write(job_file_content)

    # Now do the replacement in the job content string
    for generic, replacement in substitution_dictionary.items():
        if replacement is not None:
            job_file_content = job_file_content.replace(generic, replacement)

    if cmd_args["preserve_job_file"]:
        job_file_backup_name = job_file + "_original"
        os.rename(job_file, job_file_backup_name)
    else:
        os.remove(job_file)

    # Now that the job file has had generic substituted, write up an updated job file
    with open(job_file, "wt") as file_out:
        file_out.write(job_file_content)

    if cmd_args['run_setup']:
        # Assemble and run the job_setup command
        root = get_value("ROOT_DIR", cmd_args)
        job_dir = get_value("job_dir", cmd_args)

        if not root or not job_dir:
            logging.error("In order to run Setup ....")
        else:
            perl_path = root + "/bin/special_perl "
            job_setup = root + "/perl/job_setup.pl "
            sys_command = perl_path + job_setup + job_file + " " + job_dir
            print("Here is the Setup command -\n{}".format(sys_command))
            support_funtions.execute_command(sys_command)

    # Program Finished
    print('Script Finished')