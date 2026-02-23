# utils/db_logger.py
import threading
from automation.models import StepResult, NetworkLog


class DBLogger:

    def __init__(self, journey_run):
        self.journey_run = journey_run

    def log_step(self, step_number, test_case, passed, comment="", screenshot_path="", url=""):
        result = {}

        def _save():
            step = StepResult.objects.create(
                journey_run=self.journey_run,
                step_number=step_number,
                test_case=test_case,
                passed=passed,
                comment=comment,
                screenshot_path=screenshot_path,
                url=url
            )
            result['step'] = step

        thread = threading.Thread(target=_save)
        thread.start()
        thread.join()
        return result.get('step')

    def log_network(self, step_result, log_type, message):

        def _save():
            NetworkLog.objects.create(
                journey_run=self.journey_run,
                step_result=step_result,
                log_type=log_type,
                message=message
            )

        thread = threading.Thread(target=_save)
        thread.start()
        thread.join()