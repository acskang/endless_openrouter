# -*- coding: utf-8 -*-
# phrase/serializers/__init__.py


from .serializer_phrase import (
    MediaURLMixin,
    CacheOptimizedMixin,
    ValidationMixin,
    OptimizedRequestTableSerializer,
    OptimizedMovieTableSerializer,
    OptimizedDialogueSearchSerializer,
    OptimizedDialogueTableSerializer,
    OptimizedDialogueTableSerializer,
    LegacyMovieSerializer,
    LegacyMovieQuoteSerializer,
    LegacySearchSerializer,
    StatisticsSerializer,
    SearchAnalyticsSerializer,
    MySQLOptimizationSerializer,
    PerformanceMetricsSerializer,
    BulkDialogueUpdateSerializer,
    SearchOptimizationSerializer,
    get_optimized_serializer,
    log_serializer_performance,
)
