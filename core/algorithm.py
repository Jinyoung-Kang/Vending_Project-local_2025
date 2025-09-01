def sort_beverages_by_price(beverages: list, reverse=False):
    """음료 리스트를 가격순으로 정렬"""
    return sorted(beverages, key=lambda b: b['price'], reverse=reverse)

def sort_beverages_by_name(beverages: list, reverse=False):
    """음료 리스트를 이름순으로 정렬"""
    return sorted(beverages, key=lambda b: b['name'], reverse=reverse)

def search_beverage_by_name(beverages: list, target: str):
    """선형 탐색 방식으로 이름 검색"""
    for b in beverages:
        if b['name'] == target:
            return b
    return None