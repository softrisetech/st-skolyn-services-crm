from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 20  # Default page size
    # max_page_size = 1
    page_size_query_param = 'page_size'  # Default page size query parameter
    page_query_param = 'page'  # Default page query parameter

    def paginate_queryset(self, queryset, request, view=None):
        # Retrieve page_size and page from query parameters
        request = request.data
        page_size_param = request.get(self.page_size_query_param)
        page_param = request.get(self.page_query_param, 1)

        # Check for exact 'all' case
        if page_size_param == 'all':
            self.page_size = None # No pagination in this case
            self.page = None  # No pagination in this case
            self.all_items_count = queryset.count()
            return queryset

        # Set page_size to default or convert it to an integer
        if page_size_param and page_size_param.isdigit():
            page_size_value = int(page_size_param)
            self.page_size = page_size_value if page_size_value > 0 else self.page_size
        else:
            self.page_size = self.page_size  # Use the default

        # Convert page to an integer and validate it
        try:
            page = int(page_param)
            if page < 1:
                page = 1  # Reset to page 1 if page is 0 or negative
        except ValueError:
            page = 1  # Reset to page 1 if page is invalid

        # Handle cases where page exceeds total pages
        paginator = self.django_paginator_class(queryset, self.page_size)
        total_pages = paginator.num_pages
        if page > total_pages:
            page = 1  # Reset to page 1 if page exceeds total pages

        self.page = paginator.page(page)
        return list(self.page)

    def get_paginated_response(self, data):
        total_count = getattr(self, 'all_items_count', self.page.paginator.count if self.page else len(data))
        page_size = self.page_size if self.page_size else 'all'
        total_pages = (
            1 if page_size == 'all' else (total_count + self.page_size - 1) // int(self.page_size)
        )

        # Handle page number
        page_number = self.page.number if self.page else 1

        return {
            'items': data,
            'pagination': {
                'page': page_number,
                'page_size': page_size,
                'all_items_count': total_count,
                'total_pages': total_pages,
            },
        }
