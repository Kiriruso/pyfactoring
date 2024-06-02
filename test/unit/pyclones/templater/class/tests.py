# ruff: noqa

class C:
    clsv_1: int = 10
    clsv_2: str = "10"

    def __init__(self, v1, v2):
        self.v_1 = v1
        self.v_2 = v2

class C:
    __var_0__: int = '__const_0__'
    __var_1__: str = '__const_1__'

    def __function__(__var_2__, __var_3__, __var_4__):
        __var_2__.v_1 = __var_3__
        __var_2__.v_2 = __var_4__

# ================================ #

class C:
    def __init__(self, v1, v2):
        self.v_1 = v1
        self.v_2 = v2

        class D:
            def __init__(self):
                self.v_1 = 0

    def temp(self, v1, v2):
        return v1 + v2

class C:
    def __function__(__var_0__, __var_1__, __var_2__):
        __var_0__.v_1 = __var_1__
        __var_0__.v_2 = __var_2__

        class D:
            def __function__(__var_0__):
                __var_0__.v_1 = '__const_0__'

    def __function__(__var_0__, __var_1__, __var_2__):
        return __var_1__ + __var_2__