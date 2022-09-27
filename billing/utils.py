def incrementor():
    info = {"count": 100}
    def number():
        info["count"] += 1
        return info["count"]
    return number


def revenue_incrementor():
    info = {"count": 100}
    def number():
        info["count"] += 1
        return info["count"]
    return number