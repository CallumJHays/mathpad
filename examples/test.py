# %%


from mathpad.core import *

# constants
v = 5 * m / s

# symbols
t = "t" * seconds

# expressions
s = v * t

# symbolic functions
a = "a(t)" * m / s ** 2

## solving
# %%
v._repr_latex_()