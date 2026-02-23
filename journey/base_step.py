from abc import ABC, abstractmethod


class BaseStep(ABC):

    def __init__(self, page, journey_run, db_logger, browser_manager):
        self.page = page
        self.journey_run = journey_run
        self.db_logger = db_logger
        self.browser_manager = browser_manager

    @property
    @abstractmethod
    def step_number(self):
        """Each step must define its number"""
        pass

    @property
    @abstractmethod
    def test_case(self):
        """Each step must define its test case name"""
        pass

    @abstractmethod
    def execute(self):
        """Each step must implement its own logic here"""
        pass

    def run(self):
        """
        This is called externally.
        Runs execute(), handles screenshot and DB saving automatically.
        """
        screenshot_path = ""
        passed = False
        comment = ""

        try:
            result = self.execute()
            passed = True
            comment = result if result else "Step completed successfully"

        except Exception as e:
            passed = False
            comment = f"Step failed: {str(e)}"
            print(f"[ERROR] Step {self.step_number} - {self.test_case}: {e}")

        finally:
            # Always take screenshot regardless of pass/fail
            try:
                screenshot_path = self.browser_manager.take_screenshot(
                    f"step_{self.step_number:02d}_{self.test_case.replace(' ', '_').lower()}"
                )
            except Exception as e:
                print(f"[WARNING] Screenshot failed: {e}")

            # Always save to DB
            step_result = self.db_logger.log_step(
                step_number=self.step_number,
                test_case=self.test_case,
                passed=passed,
                comment=comment,
                screenshot_path=str(screenshot_path),
                url=self.page.url
            )

            # Save console logs for this step
            for log in self.browser_manager.console_logs:
                self.db_logger.log_network(
                    step_result=step_result,
                    log_type="console",
                    message=f"[{log['type']}] {log['text']}"
                )

            # Save network logs for this step
            for log in self.browser_manager.network_logs:
                self.db_logger.log_network(
                    step_result=step_result,
                    log_type="network",
                    message=f"{log['status']} - {log['url']}"
                )

            # Clear logs after saving so next step starts fresh
            self.browser_manager.console_logs.clear()
            self.browser_manager.network_logs.clear()

        return passed