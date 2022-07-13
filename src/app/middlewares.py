from app.metrics import django_http_requests_total_by_path_status


def simple_middleware(get_response):

    def middleware(request):
        response = get_response(request)
        django_http_requests_total_by_path_status.labels(request.path, response.status_code).inc()
        return response
    return middleware
