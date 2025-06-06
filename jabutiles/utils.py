import os
import re
from typing import Any, Type, Sequence
from contextlib import contextmanager



@contextmanager
def cwd(new_wd: str):
    if os.path.isfile(new_wd):
        new_wd = os.path.dirname(os.path.abspath(new_wd))
    
    old_wd = os.getcwd()
    os.chdir(new_wd)
    
    try:
        yield
    finally:
        os.chdir(old_wd)


def snap(value: float, multiple: float) -> float:
    """Returns the `value` rounded to the nearest `multiple`"""
    
    return multiple * round(value / multiple)


def stick(value: float, options: set[float], loop: float = None) -> int:
    """Returns the closest `option` from the given `value`.  
    `loop=value` wraps the search at the given limit.
    """
    
    setoptions = set(options)
    if loop is not None:
        setoptions.add(loop)
        value %= loop
    vmin = min(setoptions, key=lambda x: abs(x - value))
    return vmin % loop


def clamp(value: float, minmax: tuple[float, float]) -> Any:
    """Forces the `value` to be in between `minmax` range."""
    
    if value < minmax[0]:
        return minmax[0]
    if value > minmax[1]:
        return minmax[1]
    return value


def coalesce(value: Any, structure: Type) -> Type:
    """Forces the `value` type into the given `structure`"""
    
    if isinstance(value, structure):
        return value
    
    if structure == list:
        return [value]
    
    if structure == set:
        return {value,}
    
    if structure == tuple:
        return (value,)
    
    return value


# https://stackoverflow.com/questions/2150108/efficient-way-to-rotate-a-list-in-python
def shift_list(_list: list, shift: int = 0, invert: bool = False) -> list:
    """`Shift`s the `list` values by their indexes.  
    `invert=True` first inverts the list order before shifting."""
    
    seq = _list.copy()
    
    if invert:
        seq = seq[::-1]
    
    if not shift:
        return seq
    
    for s in range(abs(shift)):
        if shift < 0:
            seq.append(seq.pop(0))
        
        if shift > 0:
            seq.insert(0, seq.pop(-1))
    
    return seq


def shift_string(text: str, shift: int = 0, invert: bool = False) -> list:
    """`Shift`s the `text` chars by their positions.  
    `invert=True` first inverts the string order before shifting."""
    
    if invert:
        text = text[::-1]
    
    if not shift:
        return text
    
    shift = (shift + len(text)) % len(text)
    stext = text[-shift:] + text[:-shift]
    
    return stext


def remap_list(_list: list, order: Sequence) -> list:
    """Remaps the `list` elements by the given `order` indexes.  
    
    >>> remap_list([1, 2, 3, 4], [0, 2, 1, 3])
    >>> [1, 3, 2, 4]
    """
    
    if len(_list) != len(order):
        return _list
    return [_list[pos] for pos in order]


def match_choice(value: str, choices: list[str]) -> list[str]:
    # choices can be a list of precompiled patterns
    
    found = []
    
    for choice in choices:
        # pattern = choice.replace('x', '.')
        matcher = re.compile(f"^{choice}$")
        
        if matcher.match(value):
            found.append(choice)
    
    return found


def combine_choices(choice1: str, choice2: str) -> str:
    choice = []
    for c1, c2 in zip(choice1, choice2):
        if c1 == c2:
            choice.append(c1)
        
        elif c1 == '1' or c2 == '1':
            choice.append('1')
        
        else: # wildcards
            choice.append('.')
    
    return ''.join(choice)


