from django.contrib import admin
from .models import (
    JourneyRun, StepResult, AutoSuggestion,
    ListingData, ListingDetail, NetworkLog
)


@admin.register(JourneyRun)
class JourneyRunAdmin(admin.ModelAdmin):
    list_display = ['id', 'country_selected', 'suggestion_selected', 'passed', 'started_at', 'finished_at']
    list_filter = ['passed']
    ordering = ['-started_at']


@admin.register(StepResult)
class StepResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'test_case', 'url', 'passed', 'comment', 'executed_at']
    list_filter = ['passed', 'test_case']
    ordering = ['step_number']


@admin.register(AutoSuggestion)
class AutoSuggestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'has_map_icon', 'is_selected', 'captured_at']
    list_filter = ['is_selected', 'has_map_icon']


@admin.register(ListingData)
class ListingDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'price', 'is_selected', 'captured_at']
    list_filter = ['is_selected']


@admin.register(ListingDetail)
class ListingDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'subtitle', 'page_url', 'captured_at']


@admin.register(NetworkLog)
class NetworkLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'log_type', 'message', 'captured_at']
    list_filter = ['log_type']