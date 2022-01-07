import os
import glob
import subprocess
import logging
import threading
import queue
from inspect import isclass
from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module
from tool_runner_base import ToolRunnerBase


class ToolRunner():
    """Main module for tool runner"""

    def __init__(self):
        """Init ToolRunner"""
        self.queue = queue.Queue()
        self.tools = []
        logging.basicConfig(level=logging.DEBUG)
        self._check_environment()
        self._gather_all_tools()

    def _check_environment(self):
        """Checks the local environment for suitability"""
        self._check_tool_is_installed('Docker', 'docker --version')
        self._check_tool_is_installed('Terraform', 'terraform --version')
        self._check_tool_is_installed('Azure CLI', 'az account list')
        self._check_tool_is_installed('AWS CLI', 'aws sts get-caller-identity')

    def _check_tool_is_installed(self, tool_name, tool_cmd):
        """Check to make sure tool is installed"""
        exit_code = subprocess.call(tool_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if int(exit_code) != 0:
            raise Exception(f'"{tool_cmd}" status code is not zero; is {tool_name} installed?')

    def _get_repo_root(self):
        """Returns the test case dir"""
        return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    def _get_all_testcase_directories(self):
        """Returns all terraform directories"""
        glob_path = os.path.join(self._get_repo_root(), 'test-cases/*/*/*/*/')
        return [g for g in glob.glob(glob_path, recursive=True) if 'main.tf' in os.listdir(g)]

    def _init_terraform_dir(self, dirpath):
        """Inits the terraform dir"""
        items_in_queue = len(list(self.queue.queue))
        logging.info(f'{items_in_queue} - terraform init - {dirpath}')
        cmd = f"cd {dirpath} && terraform init && terraform plan -out=plan.out"
        subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _terraform_has_been_init(self, dirpath):
        """Checks if terraform is setup in the current dir"""
        if not os.path.isdir(os.path.join(dirpath, '.terraform')):
            return False
        if not os.path.isfile(os.path.join(dirpath, 'plan.out')):
            return False
        return True

    def _run_terraform_worker(self):
        """Terraform init queue worker"""
        while not self.queue.empty():
            dirpath = self.queue.get()
            self._init_terraform_dir(dirpath)
            self.queue.task_done()

    def _init_terraform(self):
        """Inits all terraform directories"""
        logging.info('Iterating and running terraform init in all directories')
        test_case_dirs = self._get_all_testcase_directories()
        for dirpath in [x for x in test_case_dirs if not self._terraform_has_been_init(x)]:
            self.queue.put(dirpath)
        num_workers = 25
        workers = []
        for worker in range(0, num_workers):
            workers.append(threading.Thread(target=self._run_terraform_worker, daemon=True))
        for w in workers:
            w.start()
        self.queue.join()

    def _get_tools_dir(self):
        """Returns the dir of the tools modules"""
        return os.path.join(self._get_repo_root(), 'tool_runner/tools/')

    def _gather_all_tools(self):
        """Gathers all available tools for testing"""
        for (_, module_name, _) in iter_modules([self._get_tools_dir()]):
            module = import_module(f"tools.{module_name}")
            for attribute_name in dir(module):
                attribute = getattr(module, attribute_name)
                if isclass(attribute):
                    if attribute is not ToolRunnerBase:
                        if issubclass(attribute, ToolRunnerBase):
                            self.tools.append(attribute)

    def run_all(self):
        """Runs all tools"""
        self._init_terraform()

    def run_specific_tool(self, tool_name):
        """Runs a specific tool from its tool name"""
        desired_tool = None
        for tool_class in self.tools:
            tc = tool_class()
            if tc.get_name() == tool_name:
                desired_tool = tc
        if desired_tool is None:
            raise Exception(f'The tool {tool_name} was not found')
        test_cases = self._get_all_testcase_directories()
        for tc in test_cases:
            result = desired_tool.run(tc)
            if result is not True:
                logging.error(f'{tool_name} - {os.path.basename(os.path.normpath(tc))} - invalid run')
                logging.error(tc)
            else:
                logging.info(f'{tool_name} - {os.path.basename(os.path.normpath(tc))} - complete')



if __name__ == '__main__':
    tr = ToolRunner()
    tr._init_terraform()
    # tr.run_specific_tool('cloudrail')
