from typing import Union, Any, Type, Callable
from ._tksheet_vars import *

def is_nonelike(n: Any):
    if n is None:
        return True
    if isinstance(n, str):
        return n.lower().replace(" ", "") in nonelike
    else:
        return False

def to_int(x: Any, **kwargs):
    if isinstance(x, int):
        return x
    return int(float(x))

def to_float(x: Any, **kwargs):
    if isinstance(x, float):
        return x
    if isinstance(x, str) and x.endswith('%'):
        return float(x.replace('%', "")) / 100
    return float(x)

def to_bool(val: Any, **kwargs):
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        v = val.lower()
    else:
        v = val
    if 'truthy' in kwargs:
        _truthy = kwargs['truthy']
    else:
        _truthy = truthy
    if 'falsy' in kwargs:
        _falsy = kwargs['falsy']
    else:
        _falsy = falsy
    if v in _truthy:
        return True
    elif v in _falsy:
        return False
    raise ValueError(f'Cannot map "{val}" to bool.')

def to_str(v: Any, **kwargs: dict) -> str:
    return f"{v}"

def float_to_str(v: Union[int, float], **kwargs: dict) -> str:
    if 'decimals' in kwargs and isinstance(kwargs['decimals'], int):
        if kwargs['decimals']:
            return f"{round(v, kwargs['decimals'])}"
        return f"{int(round(v, kwargs['decimals']))}"
    if v.is_integer():
        return f"{int(v)}"
    return f"{v}"

def percentage_to_str(v: Union[int, float], **kwargs: dict) -> str:
    if 'decimals' in kwargs and isinstance(kwargs['decimals'], int):
        if kwargs['decimals']:
            return f"{round(v * 100, kwargs['decimals'])}%"
        return f"{int(round(v * 100, kwargs['decimals']))}%"
    if v.is_integer():
        return f"{int(v) * 100}%"
    return f"{v * 100}%"

def bool_to_str(v: Any, **kwargs: dict) -> str:
    return f"{v}"

def int_formatter(datatypes = int,
                  format_function = to_int,
                  to_str_function = to_str,
                  **kwargs,
                  ) -> dict:
    return formatter(datatypes = datatypes,
                     format_function = format_function,
                     to_str_function = to_str_function,
                     **kwargs)

def float_formatter(datatypes = float,
                    format_function = to_float,
                    to_str_function = float_to_str,
                    decimals = 2,
                    **kwargs,
                    ) -> dict:
    return formatter(datatypes = datatypes,
                     format_function = format_function,
                     to_str_function = to_str_function,
                     decimals = decimals,
                     **kwargs)

def percentage_formatter(datatypes = float,
                         format_function = to_float,
                         to_str_function = percentage_to_str,
                         decimals = 2,
                         **kwargs,
                         ) -> dict:
    return formatter(datatypes = datatypes,
                     format_function = format_function,
                     to_str_function = to_str_function,
                     decimals = decimals,
                     **kwargs)

def bool_formatter(datatypes = bool,
                   format_function = to_bool,
                   to_str_function = bool_to_str,
                   invalid_value = "NA",
                   truthy_values = truthy,
                   falsy_values = falsy,
                   **kwargs,
                   ) -> dict:
    return formatter(datatypes = datatypes,
                     format_function = format_function,
                     to_str_function = to_str_function,
                     invalid_value = invalid_value,
                     truthy_values = truthy_values,
                     falsy_values = falsy_values,
                     **kwargs)

def formatter(datatypes,
              format_function,
              to_str_function = to_str,
              invalid_value = "NaN",
              nullable = True,
              pre_format_function = None,
              post_format_function = None,
              clipboard_function = None,
              **kwargs) -> dict:
    return {**dict(datatypes = datatypes,
                   format_function = format_function,
                   to_str_function = to_str_function,
                   invalid_value = invalid_value,
                   nullable = nullable,
                   pre_format_function = pre_format_function,
                   post_format_function = post_format_function,
                   clipboard_function = clipboard_function),
            **kwargs}

def format_data(value = "",
                datatypes = int,
                nullable = True,
                pre_format_function = None,
                format_function = to_int,
                post_format_function = None,
                **kwargs,
                ) -> Any:
    if pre_format_function:
        value = pre_format_function(value)
    if nullable and is_nonelike(value):
        value = None
    else:
        try:
            value = format_function(value, **kwargs)
        except Exception as e:
            value = f"{value}"
    if post_format_function and isinstance(value, datatypes):
        value = post_format_function(value)
    return value

def data_to_str(value = "",
                datatypes = int,
                nullable = True,
                invalid_value = "NaN",
                to_str_function = None,
                **kwargs) -> str:
    if not isinstance(value, datatypes):
        return invalid_value
    if value is None and nullable:
        return ""
    return to_str_function(value, **kwargs)

def get_data_with_valid_check(value = "", 
                              datatypes = tuple(),
                              invalid_value = "NA"):
    if isinstance(value, datatypes):
        return value
    return invalid_value

def get_clipboard_data(value = "",
                       clipboard_function = None,
                       **kwargs):
    if clipboard_function is not None:
        return clipboard_function(value, **kwargs)
    if isinstance(value, (int, float, bool)):
        return value
    return data_to_str(value, **kwargs)


class Formatter:
    def __init__(self,
                 value,
                 datatypes = int,
                 format_function = to_int,
                 to_str_function = to_str,
                 nullable = True,
                 invalid_value = "NaN",
                 pre_format_function = None,
                 post_format_function = None,
                 clipboard_function = None,
                 **kwargs,
                 ):
        if nullable:
            if isinstance(datatypes, (list, tuple)):
                datatypes = tuple({type_ for type_ in datatypes} | {type(None)})
            else:
                datatypes = (datatypes, type(None))
        elif isinstance(datatypes, (list, tuple)) and type(None) in datatypes:
            raise TypeError("Non-nullable cells cannot have NoneType as a datatype.")
        elif datatypes is type(None):
            raise TypeError("Non-nullable cells cannot have NoneType as a datatype.")
        self.kwargs = kwargs
        self.valid_datatypes = datatypes
        self.format_function = format_function
        self.to_str_function = to_str_function
        self.nullable = nullable
        self.invalid_value = invalid_value
        self.pre_format_function = pre_format_function
        self.post_format_function = post_format_function
        self.clipboard_function = clipboard_function
        try:
            self.value = self.format_data(value)
        except Exception as e:
            self.value = f"{value}"

    def __str__(self):
        if not self.valid():
            return self.invalid_value
        if self.value is None and self.nullable:
            return ""
        return self.to_str_function(self.value, **self.kwargs)

    def valid(self, value = None) -> bool:
        if value is None:
            value = self.value
        if isinstance(value, self.valid_datatypes):
            return True
        return False
    
    def format_data(self, value):
        if self.pre_format_function:
            value = self.pre_format_function(value)
        value = None if (self.nullable and is_nonelike(value)) else self.format_function(value, **self.kwargs)
        if self.post_format_function and self.valid(value):
            value = self.post_format_function(value)
        return value

    def get_data_with_valid_check(self):
        if self.valid():
            return self.value
        return self.invalid_value
    
    def get_clipboard_data(self):
        if self.clipboard_function is not None:
            return self.clipboard_function(self.value, **self.kwargs)
        if isinstance(self.value, (int, float, bool)):
            return self.value
        return self.__str__()
    
    def __eq__(self, __value: object) -> bool:
        # in case of custom formatter class
        # compare the values
        try: 
            if hasattr(__value, "value"):
                return self.value == __value.value
        except:
            pass
         # if comparing to a string, format the string and compare
        if isinstance(__value, str):
            try:
                return self.value == self.format_data(__value)
            except Exception as e:
                pass
        # if comparing to anything else, compare the values
        return self.value == __value 