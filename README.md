![Beautiful arch oscillations](https://github.com/RozbiyNick/readme-images/blob/main/arch-vibrations/5%20beautiful%20vibration.gif)

# A small example of the use of Python for scientific computing

1. [Problem formulation](https://github.com/RozbiyNick/arch-vibrations/tree/main#problem-formulation)
2. [Solution description](https://github.com/RozbiyNick/arch-vibrations/tree/main#solution-description)
3. [App demonstration](https://github.com/RozbiyNick/arch-vibrations/tree/main#app-demonstration)

## Problem formulation
The task is to solve following ***differential equation in partial derivatives*** describing vibrations of an arch:

<img src="https://github.com/RozbiyNick/readme-images/blob/main/arch-vibrations/2%20partial%20equation.jpg" height="80px" alt="Partial differential equation for arch vibrations">

![]()

Where y(x, t) - is a desired function.

This is a schematic image of the arch:

![Arch](https://github.com/RozbiyNick/readme-images/blob/main/arch-vibrations/1%20arch.jpg)

## Solution description

A transition to dimensionless coordinates and the **finite-difference method** are used and following system of ordinary differential equations is obtained:

![System of ordinary differential equations decribing arch vibrations](https://github.com/RozbiyNick/readme-images/blob/main/arch-vibrations/3%20system%20of%20equations.jpg)

Now, we have not the only desired function of 2 variables, but a set of desired functions of time:

*v<sub>i<sub>*(τ) - the speed of the i-th point,

*u<sub>i<sub>*(τ) - the position of the i-th point.

The number of equations is *2n*, where *n* is the number of points into which the arch is divided.

The system of differential equations is solved with the help of the 4th order [Runge-Kutta method](https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods).

The method is implemented in a `runge_kutta_4(...)` function that uses an instance of `ArchEquationsSystem` class being a callable object. 
When an `ArchEquationsSystem` object is called the values of derivatives of desired functions at a given moment are calculated and then used in Runge-Kutta formulas.
The values of desired functions are stored in a 2-dimensional list `.points` because adding a new element **takes constant time**.

***All calculations are carried out with the use of NumPy arrays that enhances performance drastically.***

***The implemented algorithm allows us to solve systems of differential equations of arbitrary size.***

## App demonstration

The app was developed using PyQt framework. The calculation algorithm is following:

1. User sets initial conditions and solution parameters and launches calculation
2. The program checks input data
3. The program ***generates the system of differential equations***
3. The solution is carried out ***in a separate thread*** with help of the class `SolverThread`
4. ***Recursive QTimer call*** is used for animation, because it is also an ***asynchronous task***

Let's look how beautiful the oscillations are!

Initial flexure = sin(x)

Initial speed = 0.3\*x\*cos(10*x)

<img src="https://github.com/RozbiyNick/readme-images/blob/main/arch-vibrations/4-Calculation-demo.gif" alt="Arch vibrations example 1" height="500">

The given example demonstrates solving a system of **300 differential equations** on **2500 time steps**.
