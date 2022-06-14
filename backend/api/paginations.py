from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'limit'
    max_page_size = 50
