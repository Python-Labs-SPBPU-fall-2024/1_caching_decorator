from collections import OrderedDict
from functools import wraps

class Cache():
    def __init__(self, strategy="LRU", capacity=3):
        self.cache = OrderedDict()
        if strategy not in ["LRU", "MRU", "LIFO", "FIFO"]:
            raise ValueError("Неизвестная стратегия:", strategy)
        self.strategy = strategy
        if capacity < 1:
            raise ValueError("Глубина не может быть меньше 0!")
        self.capacity = capacity

    def get(self, key):
        if key in self.cache:
            if self.strategy in ["LRU", "MRU"]: 
                self.cache.move_to_end(key)  #Перемещаем в конец
            return self.cache[key]
        return -1

    def put(self, key, value):
        if key in self.cache:
            if self.strategy != "FIFO":
                self.cache.move_to_end(key)  #Перемещаем в конец
        elif len(self.cache) >= self.capacity:
            lastFlag = False
            if self.strategy in ["MRU", "LIFO"]:
                lastFlag = True
            self.cache.popitem(last=lastFlag) 
        self.cache[key] = value

def cacher(strategy="LRU", depth=100):
    def wrapper(func):
        cache = Cache(strategy, depth)

        @wraps(func)
        def wrapped(*args, **kwargs):
            key = str(args) + str(kwargs)
            result = cache.get(key)
            if result == -1:
                value = func(*args, **kwargs)
                cache.put(key, value)
                return value
            return result   
        return wrapped
    return wrapper

def test_FIFO():
   
    @cacher(strategy="FIFO", depth=3)
    def slow_function(x):
        slow_function.calls += 1
        return (x ** x) / 2

    slow_function.calls = 0

    slow_function(5)
    slow_function(10)
    assert slow_function.calls == 2

    slow_function(10)
    assert slow_function.calls == 2

    slow_function(4)
    assert slow_function.calls == 3

    slow_function(5)
    assert slow_function.calls == 3

    slow_function(1)
    assert slow_function.calls == 4

    slow_function(5)
    assert slow_function.calls == 5

    slow_function(4)
    assert slow_function.calls == 5

    slow_function(1)
    assert slow_function.calls == 5

def test_LIFO():
   
    @cacher(strategy="LIFO", depth=3)
    def slow_function(x):
        slow_function.calls += 1
        return (x ** x) / 2

    slow_function.calls = 0

    slow_function(5)
    slow_function(10)
    assert slow_function.calls == 2

    slow_function(10)
    assert slow_function.calls == 2

    slow_function(4)
    assert slow_function.calls == 3

    slow_function(1)
    assert slow_function.calls == 4

    slow_function(5)
    assert slow_function.calls == 4

    slow_function(10)
    assert slow_function.calls == 4

    slow_function(3)
    assert slow_function.calls == 5

    slow_function(5)
    assert slow_function.calls == 5

def test_MRU():
   
    @cacher(strategy="MRU", depth=3)
    def slow_function(x):
        slow_function.calls += 1
        return (x ** x) / 2

    slow_function.calls = 0

    slow_function(5)
    slow_function(10)
    assert slow_function.calls == 2

    slow_function(4)
    assert slow_function.calls == 3

    slow_function(10)
    assert slow_function.calls == 3

    slow_function(1)
    assert slow_function.calls == 4

    slow_function(5)
    assert slow_function.calls == 4

    slow_function(10)
    assert slow_function.calls == 5

    slow_function(5)
    assert slow_function.calls == 6

def test_LRU():
   
    @cacher(strategy="LRU", depth=3)
    def slow_function(x):
        slow_function.calls += 1
        return (x ** x) / 2

    slow_function.calls = 0

    slow_function(5)
    slow_function(10)
    assert slow_function.calls == 2

    slow_function(4)
    assert slow_function.calls == 3

    slow_function(10)
    assert slow_function.calls == 3

    slow_function(4)
    assert slow_function.calls == 3

    slow_function(1)
    assert slow_function.calls == 4

    slow_function(5)
    assert slow_function.calls == 5

    slow_function(4)
    assert slow_function.calls == 5

    slow_function(10)
    assert slow_function.calls == 6

def test_invalid_strategy():
    try:
        @cacher(strategy="MUU", depth=3)
        def slow_function(x):
            pass
        assert False, "Ожидалось исключение"
    except TypeError:
        pass # Исключение поймано - это нормально

def test_independent_caches():

    @cacher(strategy="LRU", depth=3)
    def slow_function_1(x,y):
        slow_function_1.calls += 1
        return (x + y) * 2

    @cacher(strategy="MRU", depth=3)
    def slow_function_2(x, y):
        slow_function_2.calls += 1
        return x * 2 + y

    @cacher(strategy="LIFO", depth=3)
    def slow_function_3(x, y):
        slow_function_3.calls += 1
        return x + 2 * y

    # Проверяем, что функции имеют независимые кэши

    slow_function_1.calls = 0
    slow_function_2.calls = 0
    slow_function_3.calls = 0

    slow_function_1(1, 1)
    slow_function_2(2, 2)
    slow_function_3(3, 3)

    assert slow_function_1.calls == 1
    assert slow_function_2.calls == 1
    assert slow_function_3.calls == 1

    slow_function_1(2,2)
    slow_function_2(3,3)
    slow_function_3(1,1)

    assert slow_function_1.calls == 2
    assert slow_function_2.calls == 2
    assert slow_function_3.calls == 2

    slow_function_1(2,2)
    slow_function_2(2,2)
    slow_function_3(1,1)

    assert slow_function_1.calls == 2
    assert slow_function_2.calls == 2
    assert slow_function_3.calls == 2

    slow_function_1(3,3)
    slow_function_2(1, 1)
    slow_function_3(2, 2)

    assert slow_function_1.calls == 3
    assert slow_function_2.calls == 3
    assert slow_function_3.calls == 3

if __name__ == "main":
    test_LRU()
    test_MRU()
    test_LIFO()
    test_FIFO()
    test_invalid_strategy()
    test_independent_caches()