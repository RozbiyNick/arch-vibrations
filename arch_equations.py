import numpy as np


class ArchEquationsSystem:
    """Class representing the system of differential equations for arch

    The calculated values of unknown functions are stored in 2-dimensional list .points.
    The 1st half of the elements of .points is dedicated to the coordinates, and the second - to velocities.
    """

    def __init__(self, num_equations, start_flexure, start_speed, eps):
        self.number_of_equations = num_equations
        self.points = [start_flexure + start_speed]
        self.eps = eps
        self.h = np.pi/(self.number_of_equations + 1)

    def __u_t(self, coordinates_and_velocities):
        """Calculates derivatives of coordinates with respect to time"""

        return coordinates_and_velocities[self.number_of_equations:]

    def __v_t(self, coordinates_and_velocities):
        """Calculates derivatives of velocities with respect to time"""

        u = [
            np.concatenate(([-coordinates_and_velocities[0], 0], coordinates_and_velocities[:self.number_of_equations - 2])),
            np.concatenate(([0], coordinates_and_velocities[:self.number_of_equations - 1])),
            coordinates_and_velocities[:self.number_of_equations],
            np.concatenate((coordinates_and_velocities[1:self.number_of_equations], [0])),
            np.concatenate((coordinates_and_velocities[2:self.number_of_equations], [0, -coordinates_and_velocities[self.number_of_equations - 1]]))
        ]

        return -self.eps*((u[0] - 4*u[1]+6*u[2]-4*u[3]+u[4])/self.h**4 -
                         np.sin(np.arange(1, self.number_of_equations+1)*self.h)) + \
               np.sum(((u[0]-u[1])**2+(u[1]-u[2])**2)/(self.h**2) -
                      (np.cos(np.arange(0, self.number_of_equations)*self.h)**2 +
                       np.cos(np.arange(1, self.number_of_equations+1)*self.h)**2))*(u[1]-2*u[2]+u[3])/(4*np.pi*self.h)

    def __call__(self, time, coordinates_and_velocities):
        """Calculates derivatives of coordinates and velocities with respect to time"""

        return np.concatenate((self.__u_t(coordinates_and_velocities), self.__v_t(coordinates_and_velocities)))
