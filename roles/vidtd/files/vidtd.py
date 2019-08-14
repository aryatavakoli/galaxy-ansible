#!/usr/bin/env python

import argparse
import os
import re
import subprocess
import sys
import tempfile

# System-wide config file
CONFIG_FILE_DEFAULT_GLOBAL_LOCATION = "/etc/vidtd.conf"

# Per-user config file
CONFIG_FILE_DEFAULT_LOCAL_LOCATION = "~/.config/vidtd.conf"

dtd_app_path = None
dtd_config_path = None
job_config_path = None
venv_path = None

def create_config_file(path):
    new_config = open(path, 'w')
    new_config.write(
         "dtd_app: ~/galaxy/lib/galaxy/jobs/dynamic_tool_destination.py\n"
         + "job_config: ~/galaxy/job_conf.xml\n"
         + "dtd_config: ~/galaxy/config/tool_destinations.yml")
    new_config.close()

def format_dtd_output(output):

    # Strip out redundant info from DTD
    output = re.sub("\nErrors detected; config not valid!", "", output)
    output = re.sub("DEBUG:__main__:No default_priority section found in config\. Setting 'med' as default priority.\n", "", output)
    output = re.sub("DEBUG:__main__:", "", output)
    return output
                

# Get arguments and options from config file and command line, choose which to use.
def gather_arguments():
    global dtd_app_path
    global dtd_config_path
    global job_config_path
    global venv_path

    parser = argparse.ArgumentParser(description='Safely edit the dynamic tool destinations config file.')
    parser.add_argument('-t', dest='dtd_config', help='the config file to edit')
    parser.add_argument('-j', dest='job_config', help='the job config file, containing all of the destinations. usually named `job_conf.xml`.')
    parser.add_argument('-c', dest='config_file', help="The vidtd config file.")
    parser.add_argument('-d', dest='dtd_app', help="Galaxy's dynamic_tool_destination.py file. Defaults to `galaxy/server/lib/galaxy/jobs/dynamic_tool_destination.py`.")
    parser.add_argument('-v', dest='venv', help="The virtual environment that Galaxy runs in, if applicable.")
    args = parser.parse_args()

    if args.config_file != None:
        config_file_path = args.config_file
    else:  # Check the default config locations
        if os.path.isfile(CONFIG_FILE_DEFAULT_LOCAL_LOCATION):
            config_file_path = CONFIG_FILE_DEFAULT_LOCAL_LOCATION
        elif os.path.isfile(CONFIG_FILE_DEFAULT_GLOBAL_LOCATION):
            config_file_path = CONFIG_FILE_DEFAULT_GLOBAL_LOCATION
        else:
            print("No vidtd config file could be found! Creating one at `"
                  + CONFIG_FILE_DEFAULT_LOCAL_LOCATION + "`...")
            create_config_file(CONFIG_FILE_DEFAULT_LOCAL_LOCATION)
            print("You'll need to edit it with the correct file locations "
                  + "as per the file's instructions.")
            sys.exit(1)

    try:
        config_file_fd = open(config_file_path, 'r')
        config_file_contents = config_file_fd.read()
        config_file_fd.close()
    except:
        print("Failed to open config file %s. Quitting." % (config_file_path))
        sys.exit(1)

    # Put contents of config in dict
    config = {}
    line_num = 1
    for line in config_file_contents.split("\n"):
        try:
            key, value = line.split(": ", 1)
            config[key] = value
            line_num = line_num + 1
        except:
            if line != "":
                print("Error reading line %d from config file" % (line_num))

    # Check for required fields
    if "dtd_app" not in config and args.dtd_app == None:
        print("Missing `dtd_app` field in config file %s or argument list. Cannot proceed; quitting." % (config_file_path))
        sys.exit(1)
    if "dtd_config" not in config and args.dtd_config == None:
        print("Missing `dtd_config` field in config file %s or argument list. Cannot proceed; quitting." % (config_file_path))
        sys.exit(1)
    if "job_config" not in config and args.job_config == None:
        print("Missing `job_config` field in config file %s or argument list. Cannot proceed; quitting." % (config_file_path))
        sys.exit(1)
    if "venv" in config:
        venv_path = config["venv"]
    else:
        venv_path = None

    # Assign command line arguments that were specified to overwrite
    # config file.
    if args.dtd_config != None:
        dtd_config_path = args.dtd_config
    else:
        dtd_config_path = config["dtd_config"]

    if args.dtd_app != None:
        dtd_app_path = args.dtd_app
    else:
        dtd_app_path = config["dtd_app"]

    if args.job_config != None:
        job_config_path = args.job_config
    else:
        job_config_path = config["job_config"]

    if args.venv != None:
        venv_path = args.venv


def main():

    gather_arguments()

    # Quit immediately if we can't write the file.
    if (os.access(dtd_config_path, os.W_OK) == False):
        print("You don't have permission to write to %s, Quitting." % dtd_config_path)
        sys.exit(1);

    dtd_fp = open(dtd_config_path, 'r')
    dtd_config = dtd_fp.read()

    (temp_fd, temp_path) = tempfile.mkstemp()
    temp_fp = os.fdopen(temp_fd, 'w')
    temp_fp.write(dtd_config)
    temp_fp.close()

    editor = os.getenv('EDITOR', 'vi')
    print("Editing `%s` in temporary file `%s`\n" % (dtd_config_path, temp_path))

    done = False
    while (done == False):
        subprocess.call('%s %s' % (editor, temp_path), shell=True)

        try:
            if venv_path != None:
                dtd_output = subprocess.check_output('bash -c "source %s/bin/activate && /usr/bin/env python %s -c %s -j %s"' % (venv_path, dtd_app_path, temp_path, job_config_path), shell=True)
            else:
                dtd_output = subprocess.check_output('bash -c "/usr/bin/env python %s -c %s -j %s"' % (dtd_app_path, temp_path, job_config_path), shell=True)
        except:
            print("\n\n***DTD died trying to validate your changes! "
                  + "This usually means you edited something wrong.***")
            dtd_output = None

        if (dtd_output == None or "\nErrors detected; config not valid!\n" in dtd_output):
            if dtd_output != None:

                dtd_output = format_dtd_output(dtd_output)
                
                print("***DTD found the following errors in your file, "
                      + "preventing saving.***\n---\n" + dtd_output
                      + "\nYou may continue editing the file to remove the errors.")
                      
            valid_response = False
            while (not valid_response):
                print("Continue editing? Y/n (`n` cancels editing and throws away changes)")
                response = sys.stdin.readline()
                if response.lower() == "n\n":
                    done = True
                    valid_response = True
                elif response.lower() == "y\n":
                    valid_response = True
        else:
            print("Edits look good! Saving file...")

            temp_fp = open(temp_path, 'r')
            new_dtd_config = temp_fp.read()
            temp_fp.close()
            dtd_fp = open(dtd_config_path, 'w')
            dtd_fp.write(new_dtd_config)
            dtd_fp.close()
            done = True

    with open(temp_path, 'r') as f:

          os.unlink(temp_path)

    
if __name__ == "__main__":
    main()
