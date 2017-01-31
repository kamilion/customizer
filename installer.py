#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
# Run this with python2.7 or python3.
##############################################################################
"""Customizer Python Installer"""
##############################################################################
# Welcome to Customizer. This installer should execute on all platforms.
# However, it only supports linux. Windows and Apple users will be warded off.
from __future__ import print_function       # Python3 behavior by default
import os
import sys
import errno
import platform
import webbrowser
import argparse
import json
# We need to get the DEVNULL object from somewhere.
# first we'll try python2 with subprocess32, then python3's subprocess,
# finally resorting to python2's subprocess and simply opening devnull.
try:
    import subprocess32 as subprocess # python2 with subprocess32
    from subprocess32 import DEVNULL
except ImportError:
    subprocess32 = None
try:
    from subprocess import DEVNULL # python3
except ImportError:
    DEVNULL = open(os.devnull, 'wb') # python2 closes descriptor on exit.
if subprocess32 is None:
    import subprocess # python2 without subprocess32 package
# Using the python bindings, apt can do everything in one operation.
try:
    import apt # direct package manager access
except ImportError:
    apt = None # Not a recent ubuntu?


THIS_TITLE = "Customizer - Installer"
THIS_VERSION = "0.1.0"

INTRO = ("=====================================\n"
         "{0} {1}\n"
         "=====================================\n")

IS_WINDOWS = os.name == "nt"  # Detect if we're running on windows.
IS_MAC = sys.platform == "darwin"  # Detect if we're running on apple.
IS_64BIT = platform.machine().endswith("64") # Detect if we're 64-bit.
INTERACTIVE_MODE = not len(sys.argv) > 1  # CLI flags = non-interactive
PYTHON2_OK = sys.version_info >= (2, 7)  # Minimum version requirement
PYTHON3_OK = sys.version_info >= (3, 3)  # If python3 runs us

GITHUB_ROOT = "https://github.com"
GITHUB_RAW = "https://raw.githubusercontent.com"

BUILD_DEPS = ["build-essential", "debhelper"]

RUNTIME_DEPS = ["squashfs-tools", "xorriso", "x11-xserver-utils",
                "xserver-xephyr", "qemu-kvm", "policykit-1",
                "hicolor-icon-theme", "isolinux"]

GIT_REPOS = {
    "development"  : "kamilion/customizer/tree/development",
    "stable"  : "kamilion/customizer/tree/stable",
    "precise"  : "kamilion/customizer/tree/precise",
    "master"  : "kamilion/customizer",
    "oldstable" : "clearkimura/Customizer"
}

DEFAULT_REPO = "master" # a key from the dict above.

if not os.path.isfile('installer.json'):
    with open('installer.json', 'w') as CONFIG_FILE:
        CONFIGURATION_DATA = {}
        CONFIGURATION_DATA["current_repo"] = DEFAULT_REPO
        json.dump(CONFIGURATION_DATA, CONFIG_FILE)

with open('installer.json', 'r') as CONFIG_FILE:
    CONFIGURATION_DATA = json.load(CONFIG_FILE)


def switch_branch(branchname):
    """
    Switches branches on a git-based install.
    """
    try:
        code = subprocess.call(("git", "checkout", branchname))
    except OSError as errmsg:
        if errmsg.errno == errno.ENOENT:
            print("\nError: Git not found. It's either not installed or "
                  "not in the PATH environment variable like expected.")
            return
    if code == 0:
        print("\nBranch has been switched to: {0}".format(branchname))
    else:
        print("\nCustomizer could not update properly. If this is caused"
              " by edits you have made to the code you can try the repair"
              " option from the Maintenance submenu")


def perform_git_install(use_pyqt5):
    """
    Performs a git-based install.
    """
    if not IS_ROOT:
        root_warning()
    if use_pyqt5:
        run_cmd = ("make", "PYQT=5")
    else:
        run_cmd = ("make")
    try:
        code = subprocess.call(run_cmd)
    except OSError as errmsg:
        if errmsg.errno == errno.ENOENT:
            print("\nError: 'make' not found. It's either not installed or "
                  "not in the PATH environment variable like expected.")
            return
    if code == 0:
        print("\nCustomizer has been built from git.")
    else:
        print("\nCustomizer could not build properly. If this is caused"
              " by edits you have made to the code you can try the repair"
              " option from the Maintenance submenu")
    if not IS_ROOT:
        code = subprocess.call(("sudo", "make", "install"))
        if code == 0:
            print("\nCustomizer has been installed from git.")
        else:
            print("The installation has failed.")


def update_install():
    """
    Updates a git-based install.
    """
    try:
        code = subprocess.call(("git", "pull", "--ff-only"))
    except OSError as errmsg:
        if errmsg.errno == errno.ENOENT:
            print("\nError: Git not found. It's either not installed or "
                  "not in the PATH environment variable like expected.")
        return
    if code == 0:
        print("\nCustomizer has been updated")
    else:
        print("\nCustomizer could not update properly. If this is caused"
              " by edits you have made to the code you can try the repair"
              " option from the Maintenance submenu")


def reset_install(config=False, git_reset=False):
    """
    Resets the git-based install.
    """
    if config:
        try:
            os.unlink("/etc/customizer.conf")
            print("config file has been wiped.")
        except OSError as errmsg:
            if errmsg.errno == errno.ENOENT:
                pass
        except Exception as errmsg:
            print("An error occured when trying to remove the config file: "
                  "{}".format(errmsg))

    if git_reset:
        code = subprocess.call(("git", "reset", "--hard"))
        if code == 0:
            print("Customizer has been restored to the last local commit.")
        else:
            print("The repair has failed.")


def build_apt_reqs(compat=False, build_deps=True):
    """
    Returns a list of apt requirements given conditions.
    """
    to_install = []
    to_install.extend(RUNTIME_DEPS)
    if compat:
        if PYTHON3_OK:# We were run from python3, prefer newer packages.
            to_install.append("python3-pyqt4") # python3, pyqt4
        else:
            to_install.append("python-qt4") # python2, classic qt4
        if build_deps:
            to_install.extend(BUILD_DEPS)
            to_install.extend(["pyqt4-dev-tools", "qt4-linguist-tools"])
    else:
        if PYTHON3_OK: # We were run from python3, prefer newer packages.
            to_install.append("python3-pyqt5") # python3, pyqt5
        else:
            to_install.append("python-pyqt5") # python2, pyqt5
        if build_deps:
            to_install.extend(BUILD_DEPS)
            to_install.extend(["pyqt5-dev-tools", "qttools5-dev-tools"])
    return to_install


def install_apt_reqs(compat=False, build_deps=True):
    """
    Builds a list of requirements, then installs them.
    """
    install_requirements = build_apt_reqs(compat, build_deps)
    install_apt_list(install_requirements)


def install_apt_list(package_names):
    """
    Installs a list of packages via apt.
    """
    cache = apt.cache.Cache()
    if IS_ROOT:
        cache.update()
    cache.open()
    for pkg_name in package_names:
        try:
            cache = install_apt_package(cache, cache[pkg_name])
        except KeyError as errmsg:
            print("Sorry, package installation failed [{0}]".format(errmsg))
    # do packagey things
    if IS_ROOT:
        try:
            cache.commit()
        except Exception as errmsg:
            print("Sorry, package installation failed [{0}]".format(errmsg))
    else:
        print("Sorry, we won't be able to manage packages unless\n"
              "the installer is run as root. (perhaps with 'sudo !!' )")
    cache.close()


def install_apt_package(cache, pkg):
    """
    Marks a package for installation in the apt cache.
    """
    if pkg.is_installed:
        print("{0} already installed".format(pkg.fullname))
        return cache
    else:
        pkg.mark_install()
        return cache


def is_pyqt5_available():
    """
    Verifies PyQt5 availability. Returns bool or None.
    """
    try: # to import this empty module if installed.
        import PyQt4 # Contains a copyright notice for QT4.
    except ImportError:
        PyQt4 = None # PyQt4 is not currently installed.
    try: # to import this empty module if installed.
        import PyQt5 # Contains a copyright notice for QT5.
    except ImportError:
        PyQt5 = None # PyQt5 is not currently installed.
    if not PyQt4:
        return None
    elif not PyQt5:
        return False
    else:
        return True


def requirements_menu():
    """
    Prints a apt requirements menu.
    """
    clear_screen()
    while True:
        print(INTRO.format(THIS_TITLE, THIS_VERSION))
        print("Main requirements:\n")
        print("1. Try installing PyQt4 from apt")
        print("2. Try installing PyQt5 from apt")
        print("\n0. Go back")
        choice = user_choice()
        if choice == "1":
            install_apt_reqs(compat=True)
            wait()
        elif choice == "2":
            install_apt_reqs(compat=False)
            wait()
        elif choice == "0":
            break
        clear_screen()


def update_menu():
    """
    Prints a update menu.
    """
    clear_screen()
    while True:
        print(INTRO.format(THIS_TITLE, THIS_VERSION))
        root_warning()
        reqs = is_pyqt5_available()
        if reqs is None:
            status = "No requirements installed"
        elif reqs is False:
            status = "GUI requirements installed (PyQT4)"
        else:
            status = "GUI requirements installed (PyQT5)"
        print("Status: " + status + "\n")
        print("Update:\n")
        print("Customizer:")
        print("1. Update Customizer (recommended)")
        print("2. Update Customizer + update apt requirements")
        print("\nOthers:")
        print("3. Update requirements")
        print("\n0. Go back")
        choice = user_choice()
        if choice == "1":
            update_install()
            wait()
        elif choice == "2":
            update_install()
            print("Updating requirements...")
            reqs = is_pyqt5_available()
            if reqs is not None:
                install_apt_reqs(compat=reqs)
            else:
                print("The requirements haven't been installed yet.")
            wait()
        elif choice == "3":
            reqs = is_pyqt5_available()
            if reqs is not None:
                install_apt_reqs(compat=reqs)
            else:
                print("The requirements haven't been installed yet.")
            wait()
        elif choice == "0":
            break
        clear_screen()


def repo_menu():
    """
    Prints a repo menu.
    """
    clear_screen()
    while True:
        print(INTRO.format(THIS_TITLE, THIS_VERSION))
        print("Current Repo: " + CONFIGURATION_DATA["current_repo"])
        current_repo_url = GITHUB_ROOT + "/" + GIT_REPOS[CONFIGURATION_DATA["current_repo"]]
        print("Current Repo URL: " + current_repo_url)
        reqs = is_pyqt5_available()
        if reqs is None:
            status = "No requirements found to be installed"
        elif reqs is False:
            status = "GUI requirements installed (PyQT4)"
        else:
            status = "GUI requirements installed (PyQT5)"
        print("Status: " + status + "\n")
        print("Update:\n")
        print("Customizer:")
        print("1. Change Repository (A list will be printed)")
        print("2. Visit repo in web browser")
        print("3. Switch to selected repository")
        print("\n0. Go back")
        choice = user_choice()
        if choice == "1":
            CONFIGURATION_DATA["current_repo"] = change_repo_menu()
            with open('installer.json', 'w') as config_file:
                json.dump(CONFIGURATION_DATA, config_file)
        elif choice == "2":
            webbrowser.open(current_repo_url)
        elif choice == "3":
            print("Switching currently checked out branch...")
            switch_branch(CONFIGURATION_DATA["current_repo"])
            wait()
        elif choice == "0":
            break
        clear_screen()


def change_repo_menu():
    """
    Prints a list of repos to choose from.
    """
    clear_screen()
    while True:
        print(INTRO.format(THIS_TITLE, THIS_VERSION))
        repo = CONFIGURATION_DATA["current_repo"]
        print("Current Repo: " + repo)
        current_repo_url = GITHUB_ROOT + "/" + GIT_REPOS[repo]
        print("Current Repo URL: " + current_repo_url)
        reqs = is_pyqt5_available()
        if reqs is None:
            status = "No requirements found to be installed"
        elif reqs is False:
            status = "GUI requirements installed (PyQT4)"
        else:
            status = "GUI requirements installed (PyQT5)"
        print("Status: " + status + "\n")
        print("Update:\n")
        print("Customizer:")
        print("1. Switch to stable repo (recommended)")
        print("2. Switch to master repo")
        print("3. Switch to devel repo")
        print("\nOthers:")
        print("4. Switch to ubuntu precise repo (Compatibility)")
        print("5. Switch to old stable repo (Compatibility)")
        print("\n0. Go back")
        choice = user_choice()
        if choice == "1":
            return "stable"
        elif choice == "2":
            return "master"
        elif choice == "3":
            return "development"
        elif choice == "4":
            return "precise"
        elif choice == "5":
            return "oldstable"
        else:
            return repo
        clear_screen()


def maintenance_menu():
    """
    Prints a maintinence menu.
    """
    clear_screen()
    while True:
        print(INTRO.format(THIS_TITLE, THIS_VERSION))
        root_warning()
        print("Maintenance:\n")
        print("1. Repair Customizer (discards code changes, keeps data intact)")
        print("2. Wipe config file (all settings removed, keeps data intact)")
        print("3. Factory reset (all of the above)")
        print("\n0. Go back")
        choice = user_choice()
        if choice == "1":
            print("Any code modification you have made will be lost. Data/"
                  "project settings will be left intact. Are you sure?")
            if user_pick_yes_no():
                reset_install(git_reset=True)
                wait()
        elif choice == "2":
            print("Are you sure? This will wipe the config file, which "
                  "contains all your project settings.")
            if user_pick_yes_no():
                reset_install(config=True)
                wait()
        elif choice == "3":
            print("Are you sure? This will remove your installation "
                  "data.\nYou'll lose any modifications you have made.\n"
                  "There is no going back.")
            if user_pick_yes_no():
                reset_install(config=True, git_reset=True)
                wait()
        elif choice == "0":
            break
        clear_screen()


def unix_which(program):
    """
    Locates an installed tool on the filesystem if it's in the path.
    """
    def is_exe(fpath):
        """Is this executable?"""
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def run_app(interpreter):
    """
    Starts the installed application with the interpreter specified.
    """
    if interpreter is None: # This should never realistically happen
        raise RuntimeError("Couldn't find specified Python interpreter")

    if is_pyqt5_available() is None:
        print("You don't have the requirements to start Customizer.\n"
              "Install them from the interactive menu.")
        if not INTERACTIVE_MODE:
            exit(1)

    cmd = (interpreter, unix_which("customizer-gui"))

    print("Starting Customizer with {0}...".format(cmd))
    while True:
        try:
            code = subprocess.call(cmd)
        except KeyboardInterrupt:
            code = 0
            break
        else:
            if code == 0:
                break

    print("Customizer has terminated. Exit code: %d" % code)

    if INTERACTIVE_MODE:
        wait()


def clear_screen():
    """
    Clears the screen before printing an interactive menu.
    """
    if IS_WINDOWS:
        os.system("cls")
    else:
        os.system("clear")


def wait():
    """
    Waits for a user to press a key to continue.
    """
    if INTERACTIVE_MODE:
        user_choice_compat("Press enter to continue.")


def user_choice_compat(prompt):
    """
    Requests a alphanumeric response from the user.
    This function will hide python3's changing of input
    from raw_input in python2. The semantics are the same.
    """
    if PYTHON3_OK:
        return input(prompt).strip()
    else:
        return raw_input(prompt).strip()


def user_choice(prompt="> ", lower=True):
    """
    Requests a alphanumeric response from the user.
    This function will hide python3's changing of input
    from raw_input in python2. The semantics are the same.
    """
    if lower:
        return user_choice_compat(prompt).lower()
    else:
        return user_choice_compat(prompt)


def user_pick_yes_no():
    """
    Requests an affirmative or negative from the user.
    This function will hide python3's changing of input
    from raw_input in python2. The semantics are the same.
    Returns the user's choice.
    """
    choice = None
    pick_yes = ("yes", "y")
    pick_no = ("no", "n")
    while choice not in pick_yes and choice not in pick_no:
        choice = user_choice("Yes/No > ")
    return choice in pick_yes


def remove_readonly(func, path):
    """
    Attempt to remove read only flags before unlink with broad perms.
    Returns nothing.
    """
    os.chmod(path, 0o755)
    func(path)


if not IS_WINDOWS:
    if os.geteuid() != 0:
        IS_ROOT = False
    else:
        IS_ROOT = True
else:
    IS_ROOT = False


def root_warning():
    """
    Print a helpful message when root access is unavailable.
    Returns nothing.
    """
    if IS_ROOT:
        print(u"Root account: is available.")
    else:
        print(u"Root account: is not available.")
        print("Sorry, we won't be able to directly manage packages unless\n"
              "the installer is run as root. (perhaps with 'sudo !!')\n"
              "\nHowever we'll try to sudo commands if possible.\n")


def platform_warning():
    """
    Print a helpful message when an unsupported platform is used.
    Returns nothing.
    """
    if IS_MAC:
        print("Sorry, your Macintosh platform isn't supported.\n\n")
    elif IS_WINDOWS:
        print("Sorry, your Windows platform isn't supported.\n\n")


def tool_check(tool, was_found=False, critical=False):
    """
    Print a message when a tool is missing. Returns nothing.
    """
    if was_found:
        print(u"Tool: '{0}' is available.".format(tool))
    else:
        tool_warning(tool, critical)


def tool_warning(tool, critical=False):
    """
    Print a message when a tool is missing. Returns nothing.
    """
    if not critical:
        print(u"Tool: '{0}' is not available.".format(tool))
    else:
        print("WARNING: '{0}' not found. This means that it's either not "
              "installed\nor not in the PATH environment variable like "
              "requested in the guide.\n".format(tool))


def is_tool_installed(tool):
    """
    Checks if a tool is installed. Returns bool.
    """
    try:
        subprocess.call([tool, "--version"], stdout=DEVNULL,
                        stdin=DEVNULL, stderr=DEVNULL)
    except OSError as errmsg:
        if errmsg.errno == errno.ENOENT:
            return False
        else:
            raise
    else:
        return True


GIT_INSTALLED = is_tool_installed("git") # We need git.
PIP_INSTALLED = is_tool_installed("pip") # pip is nice.
APT_INSTALLED = is_tool_installed("apt") # New ubuntu?
APTGET_INSTALLED = is_tool_installed("apt-get") # Ubuntu?
DPKG_INSTALLED = is_tool_installed("dpkg") # Debian-derived?
RPM_INSTALLED = is_tool_installed("rpm") # Redhat


def main_menu():
    """
    Prints the main interactive menu.
    """
    print("Verifying git installation...")
    is_git_installation = os.path.isdir(".git")
    clear_screen()

    while True:
        print(INTRO.format(THIS_TITLE, THIS_VERSION))
        root_warning()
        if apt is None: # This will be printed users lacking apt.
            print("Customizer installer cannot interact with the\n"
                  "ubuntu package manager without the apt module!\n")
        if not is_git_installation:
            print("WARNING: It doesn't look like Customizer has been "
                  "installed with git.\nThis means that you won't "
                  "be able to use this script to update or change\n"
                  "which repository you're currently using.\n")
        platform_warning()

        print("\nTool status:")
        tool_check("git", GIT_INSTALLED) # Always check git.
        if not IS_WINDOWS or IS_MAC: # no further tools are needed.
            tool_check("dpkg", DPKG_INSTALLED, critical=True)
            tool_check("apt-get", APTGET_INSTALLED, critical=True)
            tool_check("apt", APT_INSTALLED)
            tool_check("rpm", RPM_INSTALLED, critical=False)

        print("\n")
        if not IS_WINDOWS or IS_MAC:
            print("1. Run Customizer")
            print("2. Install Customizer")
            print("3. Install GUI requirements with apt")
        if GIT_INSTALLED and is_git_installation:
            print("4. Update from Github")
        if GIT_INSTALLED:
            print("5. Change Repo or branch")
        print("6. Maintenance (repair, reset...)")
        print("\n0. Quit")
        choice = user_choice()

        if choice == "1":
            run_app(interpreter=sys.executable)
        elif choice == "2":
            perform_git_install(is_pyqt5_available())
            wait()
        elif choice == "3":
            requirements_menu()
        elif choice == "4":
            update_menu()
        elif choice == "5":
            repo_menu()
        elif choice == "6":
            maintenance_menu()
        elif choice == "0":
            break
        clear_screen()


def parse_cli_arguments():
    """
    Parses CLI arguments and returns them.
    """
    parser = argparse.ArgumentParser(description="Customizer's Installer")
    parser.add_argument("--start", "-s",
                        help="Starts Customizer-gui",
                        action="store_true")
    parser.add_argument("--update-customizer",
                        help="Updates customizer (git)",
                        action="store_true")
    parser.add_argument("--update-build-reqs",
                        help="Updates build requirements",
                        action="store_true")
    parser.add_argument("--update-reqs",
                        help="Updates runtime requirements",
                        action="store_true")
    parser.add_argument("--repair",
                        help="Issues a git reset --hard",
                        action="store_true")
    return parser.parse_args()


# Functions from this file may be imported or executed from python.
# The status of tools may be found after import by examining the module.
# If we're executed as the main file, the following code is ran.
if __name__ == '__main__':
    SCRIPT_PATH = os.path.abspath(__file__)
    SCRIPT_DIRNAME = os.path.dirname(SCRIPT_PATH)
    # Sets current directory to the script's
    os.chdir(SCRIPT_DIRNAME)
    CLI_ARGS = parse_cli_arguments()
    if not (PYTHON2_OK or PYTHON3_OK):
        print("Fatal Error: Customizer needs Python 2.7 or superior.\n"
              "Installation of the minimum version is required.\n"
              "Press enter to continue.") # Really old pythons?
        if INTERACTIVE_MODE:
            wait()
        exit(1)
    if CLI_ARGS.repair:
        reset_install(git_reset=True)
    if CLI_ARGS.update_customizer:
        update_install()
    if CLI_ARGS.update_reqs:
        install_apt_reqs(compat=True)
    elif CLI_ARGS.update_build_reqs:
        install_apt_reqs(compat=False)
    if INTERACTIVE_MODE:
        main_menu()
    elif CLI_ARGS.start:
        run_app(interpreter=sys.executable)
