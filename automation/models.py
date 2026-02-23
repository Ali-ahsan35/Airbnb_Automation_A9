from django.db import models

class JourneyRun(models.Model):
    """One record per full automation run"""
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    country_selected = models.CharField(max_length=100, blank=True)
    suggestion_selected = models.CharField(max_length=200, blank=True)
    passed = models.BooleanField(default=False)

    def __str__(self):
        return f"Run #{self.id} | {self.started_at.strftime('%Y-%m-%d %H:%M')} | {'PASSED' if self.passed else 'FAILED'}"

    class Meta:
        ordering = ['-started_at']


class StepResult(models.Model):
    """One record per step/test case"""
    journey_run = models.ForeignKey(
        JourneyRun, on_delete=models.CASCADE, related_name='steps'
    )
    step_number = models.IntegerField()
    test_case = models.CharField(max_length=200)
    url = models.URLField(max_length=500, blank=True)
    passed = models.BooleanField(default=False)
    comment = models.TextField(blank=True)
    screenshot_path = models.CharField(max_length=500, blank=True)
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = 'PASSED' if self.passed else 'FAILED'
        return f"Step {self.step_number} | {self.test_case} | {status}"

    class Meta:
        ordering = ['step_number']


class AutoSuggestion(models.Model):
    """Stores suggestions captured """
    journey_run = models.ForeignKey(
        JourneyRun, on_delete=models.CASCADE, related_name='suggestions'
    )
    text = models.CharField(max_length=300)
    has_map_icon = models.BooleanField(default=False)
    is_selected = models.BooleanField(default=False)  # which one was clicked
    captured_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.text} | {'Selected' if self.is_selected else ''}"


class ListingData(models.Model):
    """Stores scraped listings """
    journey_run = models.ForeignKey(
        JourneyRun, on_delete=models.CASCADE, related_name='listings'
    )
    title = models.CharField(max_length=500)
    price = models.CharField(max_length=100, blank=True)
    image_url = models.URLField(max_length=1000, blank=True)
    is_selected = models.BooleanField(default=False)  # which one was clicked
    captured_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} | {self.price}"


class ListingDetail(models.Model):
    """Stores detail page data """
    journey_run = models.ForeignKey(
        JourneyRun, on_delete=models.CASCADE, related_name='listing_details'
    )
    title = models.CharField(max_length=500)
    subtitle = models.CharField(max_length=500, blank=True)
    image_urls = models.JSONField(default=list)  # stores list of image URLs
    page_url = models.URLField(max_length=1000, blank=True)
    captured_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"


class NetworkLog(models.Model):
    """Stores console and network logs"""
    LOG_TYPES = [
        ('console', 'Console'),
        ('network', 'Network'),
    ]
    journey_run = models.ForeignKey(
        JourneyRun, on_delete=models.CASCADE, related_name='network_logs'
    )
    step_result = models.ForeignKey(
        StepResult, on_delete=models.CASCADE, 
        related_name='logs', null=True, blank=True
    )
    log_type = models.CharField(max_length=20, choices=LOG_TYPES)
    message = models.TextField()
    captured_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.log_type} | {self.message[:50]}"
