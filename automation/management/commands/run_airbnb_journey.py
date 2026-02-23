# automation/management/commands/run_airbnb_journey.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from automation.models import JourneyRun
from journey.browser import BrowserManager
from utils.db_logger import DBLogger


class Command(BaseCommand):
    help = 'Run the Airbnb end-to-end user journey automation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--headless',
            action='store_true',
            help='Run browser in headless mode (no UI)',
        )

    def handle(self, *args, **options):
        headless = options['headless']

        self.stdout.write(self.style.NOTICE('Starting Airbnb Journey Automation...'))

        # Step 1: Create a new journey run record
        journey_run = JourneyRun.objects.create()
        self.stdout.write(f'Journey Run #{journey_run.id} created')

        # Step 2: Start the browser
        browser_manager = BrowserManager(headless=headless)
        page = browser_manager.start()
        self.stdout.write('Browser started')

        # Step 3: Create DB logger
        db_logger = DBLogger(journey_run=journey_run)

        # Step 4: Shared context between steps
        # (country, suggestion, dates, guests — passed between steps)
        context = {}

        # Step 5: Run all steps in order
        all_passed = True
        try:
            # Do this — lazy imports, only load what exists:
            steps = []

            from journey.step01_landing import Step01Landing
            steps.append(Step01Landing(page, journey_run, db_logger, browser_manager, context))

            steps = [
                Step01Landing(page, journey_run, db_logger, browser_manager, context),
            ]

            for step in steps:
                self.stdout.write(f'Running Step {step.step_number}: {step.test_case}...')
                passed = step.run()

                if passed:
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Step {step.step_number} PASSED'))
                else:
                    self.stdout.write(self.style.ERROR(f'  ✗ Step {step.step_number} FAILED'))
                    all_passed = False

                # Save shared context data to journey run after each step
                import threading
                if step.step_number == 1:
                    def _save_country():
                        from automation.models import JourneyRun
                        JourneyRun.objects.filter(id=journey_run.id).update(
                            country_selected=context.get('country', '')
                        )
                    t = threading.Thread(target=_save_country)
                    t.start()
                    t.join()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Fatal error: {e}'))
            all_passed = False

        finally:
            # Always stop browser and update journey run
            browser_manager.stop()
            journey_run.finished_at = timezone.now()
            journey_run.passed = all_passed
            journey_run.save()

            self.stdout.write('Browser stopped')

        # Final result
        if all_passed:
            self.stdout.write(self.style.SUCCESS('Journey PASSED ✓'))
        else:
            self.stdout.write(self.style.ERROR('Journey FAILED ✗'))