# mathpad

<!-- TODO: set up all the services needed for these badges -->
<!-- <p align="center">
  <a href="https://github.com/CallumJHays/mathpad/actions?query=workflow%3ACI">
    <img src="https://img.`sh`ields.io/github/workflow/status/CallumJHays/mathpad/CI/main?label=CI&logo=github&style=flat-square" alt="CI Status" >
  </a>
  <a href="https://mathpad.readthedocs.io">
    <img src="https://img.shields.io/readthedocs/mathpad.svg?logo=read-the-docs&logoColor=fff&style=flat-square" alt="Documentation Status">
  </a>
  <a href="https://codecov.io/gh/CallumJHays/mathpad">
    <img src="https://img.shields.io/codecov/c/github/CallumJHays/mathpad.svg?logo=codecov&logoColor=fff&style=flat-square" alt="Test coverage percentage">
  </a>
</p>
<p align="center">
  <a href="https://python-poetry.org/">
    <img src="https://img.shields.io/badge/packaging-poetry-299bd7?style=flat-square&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAASCAYAAABrXO8xAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAJJSURBVHgBfZLPa1NBEMe/s7tNXoxW1KJQKaUHkXhQvHgW6UHQQ09CBS/6V3hKc/AP8CqCrUcpmop3Cx48eDB4yEECjVQrlZb80CRN8t6OM/teagVxYZi38+Yz853dJbzoMV3MM8cJUcLMSUKIE8AzQ2PieZzFxEJOHMOgMQQ+dUgSAckNXhapU/NMhDSWLs1B24A8sO1xrN4NECkcAC9ASkiIJc6k5TRiUDPhnyMMdhKc+Zx19l6SgyeW76BEONY9exVQMzKExGKwwPsCzza7KGSSWRWEQhyEaDXp6ZHEr416ygbiKYOd7TEWvvcQIeusHYMJGhTwF9y7sGnSwaWyFAiyoxzqW0PM/RjghPxF2pWReAowTEXnDh0xgcLs8l2YQmOrj3N7ByiqEoH0cARs4u78WgAVkoEDIDoOi3AkcLOHU60RIg5wC4ZuTC7FaHKQm8Hq1fQuSOBvX/sodmNJSB5geaF5CPIkUeecdMxieoRO5jz9bheL6/tXjrwCyX/UYBUcjCaWHljx1xiX6z9xEjkYAzbGVnB8pvLmyXm9ep+W8CmsSHQQY77Zx1zboxAV0w7ybMhQmfqdmmw3nEp1I0Z+FGO6M8LZdoyZnuzzBdjISicKRnpxzI9fPb+0oYXsNdyi+d3h9bm9MWYHFtPeIZfLwzmFDKy1ai3p+PDls1Llz4yyFpferxjnyjJDSEy9CaCx5m2cJPerq6Xm34eTrZt3PqxYO1XOwDYZrFlH1fWnpU38Y9HRze3lj0vOujZcXKuuXm3jP+s3KbZVra7y2EAAAAAASUVORK5CYII=" alt="Poetry">
  </a>
  <a href="https://github.com/ambv/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="black">
  </a>
  <a href="https://github.com/pre-commit/pre-commit">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat-square" alt="pre-commit">
  </a>
</p>
<p align="center">
  <a href="https://pypi.org/project/mathpad/">
    <img src="https://img.shields.io/pypi/v/mathpad.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPI Version">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/mathpad.svg?style=flat-square&logo=python&amp;logoColor=fff" alt="Supported Python versions">
  <img src="https://img.shields.io/pypi/l/mathpad.svg?style=flat-square" alt="License">
</p> -->

`mathpad` is a robust Computer Algebra System (CAS) library built on top of `SymPy`, providing a simple and intuitive way to solve engineering, science, and math problems using Python.

## Quickstart
1. Install using package manager of choice. For example, `pip`:

```bash
pip install mathpad
```

2. Import and use the library in `python`:

  <table style="width: 100%;">
  <tr>
  <td> Code </td> <td> Display </td>
  </tr>
  <tr>
  <td>

  ```python
  from mathpad import *

  v = 5 * m / s

  mph = "mph" * miles / hour
  eqn = mph == v.eval()
  ```

  </td>
  <td>

  ![Alt text](examples/imgs/showcase/basic.png)

  </td>
  </tr>
  </table>


## Documentation

Currently the only in-depth documentation is `Walkthrough.ipynb`. You can access it on the [JupyterLite Sandbox Site here](https://callumjhays.github.io/mathpad/lab?path=Walkthrough.ipynb). 


## Showcase

<table style="width: 100%;">
<col style="width: 10%" />
<col style="width: 45%" />
<col style="width: 45%" />

<tr>
<td>Feature</td> <td>Example</td> <td> Display </td>
</tr>
<tr>
<td>Units</td>
<td>

```python
m

m / s ** 2

feet.in_units(cm)

(V * A).in_units(watt)
```

</td>
<td>

![Alt text](examples/imgs/showcase/units.png)

</td>
</tr>
<tr>
<td>Values</td>
<td>

```python
v = 2.5 * m / s

c = m(5)
```

</td>
<td>

![Alt text](examples/imgs/showcase/values.png)

</td>
</tr>
<tr>
<td>Symbols</td>
<td>

```python
t = "t" * seconds

y = "\\hat{y}_1" * volts
```

</td>
<td>

![Alt text](examples/imgs/showcase/symbols.png)

</td>
</tr>
<tr>
<td>Symbolic Functions</td>
<td>

```python
a = "a(t)" * m / s ** 2
```

</td>
<td>

![Alt text](examples/imgs/showcase/sym-funcs.png)

</td>
</tr>
<tr>
<td>Equations</td>
<td>

```python
eqn = (v == a * t)
```

</td>
<td>

![Alt text](examples/imgs/showcase/equations.png)

</td>
</tr>
<tr>
<td>Solving</td>
<td>

```python
sln, = solve([eqn], solve_for=[a])

sln[a]
```

</td>
<td>

![Alt text](examples/imgs/showcase/solving.png)

</td>
</tr>
<tr>
<td>Algebra</td>
<td>

```python

simplify(e ** (1j * pi))

expand((t + 1)(t + 2))

factor(t**2 + 3 * t * s + 2)

subs((t + 1)(t + 2), { t: 5 })
```

</td>
<td>

![Alt text](examples/imgs/showcase/algebra.png)

</td>
</tr>
<tr>
<td>Calculus</td>
<td>

```python
diff(a, wrt=t, order=1)


integral(a, wrt=t, between=(0, 10))
```

</td>
<td>

![Alt text](examples/imgs/showcase/calculus.png)

</td>
</tr>
<tr>
<td>Vectors</td>
<td>

```python
O = R3("O") # 3D frame of reference
v1 = O[1, 2, 3]


x, y, z = ("x", "y", "z") * m
v2 = O[x, y, z]



v3 = "v_3" @ O



v2.cross(v3)
```

</td>
<td>

![Alt text](examples/imgs/showcase/vectors.png)

</td>
</tr>
<tr>
<td>Matrices</td>
<td>

```python
O2 = R2("O2")
A = Mat[O, O2](
    [1, 2],
    [3, 4],
    [5, 6]
)


v2_wrt_O2 = v2 @ A


B = Mat[O2, O]("B")


I = Mat[O2, O2].I
```

</td>
<td>

![Alt text](examples/imgs/showcase/matrices.png)

</td>
</tr>
<tr>
<td>Numpy Compatibility</td>
<td>

```python
y = sin(t)
y_fn = as_numpy_func(y)

y_fn({ t: [1, 2, 3] })

import numpy as np
y_fn({
  t: np.arange(
    start=0, stop=2 * np.pi, step=np.pi / 12
  )
})
```

</td>
<td style="font-family: Consolas;">
<br />

array([0.84147098, 0.90929743, 0.14112001])
<br />
<br />
<br />

array([0.        , 0.25881905, 0.5       , 0.70710678, 0.8660254 ,
       0.96592583, 1.        , 0.96592583, 0.8660254 , 0.70710678,
       0.5       , 0.25881905])

</td>
</tr>
<tr>
</td>
</tr>
<tr>
<td>Code Generation</td>
<td>

```python

generate_c_code(theta, [t])
```

</td>
<td>



</td>
</tr>


</table>



<!-- ## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)): -->

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

<!-- This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome! -->

## Credits

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[browniebroke/cookiecutter-pypackage](https://github.com/browniebroke/cookiecutter-pypackage)
project template.
