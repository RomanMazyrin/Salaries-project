from prometheus_client import Counter

django_http_requests_total_by_path_status = Counter(
    'django_http_requests_total_by_path_status',
    'Number of requests per path with response statuses',
    ['path', 'status']
)

