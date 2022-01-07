from abc import ABC, abstractmethod
import os
import subprocess


class ToolRunnerBase(ABC):
    """Base class for tool runner"""

    def setup(self):
        """Sets up the tool"""
        logging.info(f'Setting up {self.get_name()}')
        self._check_required_env_vars_are_present()
        cmd_output = subprocess.call(self.get_setup_command(), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def run(self, dirpath):
        """Runs the tool on the test case
        Returns bool whether or not the run was successful"""
        cmd_output = subprocess.call(self.get_run_command(), shell=True)
        return self._check_if_run_was_successful(dirpath, cmd_output)

    def _check_if_run_was_successful(self, dirpath, cmd_output):
        """Checks if run was successful"""
        if not os.path.isfile(os.path.join(dirpath, self.get_results_file_name())):
            return False
        if int(cmd_output) not in self.get_acceptable_status_codes():
            return False
        return True

    def _check_required_env_vars_are_present(self):
        """Checks that all required environment variables are present"""
        for var in self.get_required_env_vars():
            if not os.environ.get(var):
                raise Exception(f'{var} environment variable is required for {self.get_name()}')

    # def _check_tool_version(self):
    #     """Checks and returns the current tool's version"""
    #     cmd_output = subprocess.call(self.get_version_command(), shell=True, stdout=, stderr=subprocess.DEVNULL) 

    @abstractmethod
    def get_name(self):
        """Returns the simple name of the tool"""
        pass

    def get_name_pretty(self):
        """Returns the pretty name of the tool"""
        return self.get_name()

    @abstractmethod
    def get_run_command(self):
        """Returns the run command of the tool"""
        pass

    @abstractmethod
    def get_version_command(self):
        """Returns the version command of the tool"""
        pass

    @abstractmethod
    def get_setup_command(self):
        """Returns the setup command of the tool"""
        pass

    @abstractmethod
    def get_acceptable_status_codes(self):
        """Returns the acceptable status of the tool that indicates
        that the tool ran correctly, regardless of results"""
        pass

    @abstractmethod
    def get_required_env_vars(self):
        """Returns the environment variable names (without the $)
        that the tool needs in order to run"""
        pass

    @abstractmethod
    def get_results_file_name(self):
        """Returns the name of the results file the tool saves things to
        within the test case directory (example tool_results.txt)"""
        pass
