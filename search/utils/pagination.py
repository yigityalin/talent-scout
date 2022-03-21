from github.PaginatedList import PaginatedList
from typing import List


class CombinedPaginatedList:
    def __init__(self, paginated_lists: List[PaginatedList]):
        self.paginated_lists = paginated_lists
        self._page_order = None
        self.current_page = 0
        self._max_paginated_list_length = None
        self._totalCount = None

    def _order_pages(self):
        return [
            (list_number, page_number)
            for page_number in range(self.max_paginated_list_length)
            for list_number in range(self.paginated_list_count)
            if page_number < (self.paginated_lists[list_number].totalCount / 30)
        ]

    @property
    def page_order(self):
        if not self._page_order:
            self._page_order = self._order_pages()
        return self._page_order

    @property
    def paginated_list_count(self) -> int:
        return len(self.paginated_lists)

    @property
    def totalCount(self):
        if not self._totalCount:
            self._totalCount = sum(paginated_list.totalCount for paginated_list in self.paginated_lists)
        return self._totalCount

    @property
    def max_paginated_list_length(self):
        if not self._max_paginated_list_length:
            self._max_paginated_list_length = max(paginated_list.totalCount / 30
                                                  for paginated_list in self.paginated_lists)
        return self._max_paginated_list_length

    def get_page(self, page_number: int) -> list:
        page, list_index = divmod(page_number, self.paginated_list_count)
        paginated_list = self.paginated_lists[list_index]
        return paginated_list.get_page(page)
