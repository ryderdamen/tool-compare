from tool_runner_base import ToolRunnerBase


class CloudrailRunner(ToolRunnerBase):
    """Runner class for Cloudrail"""

    def get_name(self):
        return 'cloudrail'

    def get_name_pretty(self):
        return 'Cloudrail'

    def get_run_command(self):
        return 'docker run --rm $IT_FLAG -u 0:0 -v $PWD:/data -e CLOUDRAIL_API_KEY indeni/cloudrail-cli run --tf-plan plan.out --output-file cloudrail_results.txt --no-cloud-account --auto-approve -v'

    def get_setup_command(self):
        return 'docker pull indeni/cloudrail-cli:latest'

    def get_version_command(self):
        return "docker run -t -v $PWD:/tf indeni/cloudrail-cli --version | awk '{print $NF}' | head -n 1"

    def get_required_env_vars(self):
        return [
            'CLOUDRAIL_API_KEY',
        ]

    def get_acceptable_status_codes(self):
        return [0]

    def get_results_file_name(self):
        return 'cloudrail_results.txt'
