import numpy as np


def runge_kutta_4(system_of_diff_equations, max_value_of_independent_variable, number_of_steps,
                  update_progress_signal=None):
    """Solves the given system of differential equations with the 4th order Runge-Kutta method"""

    np.seterr('raise')
    half_step_size = max_value_of_independent_variable / number_of_steps / 2

    try:
        for j in range(1, number_of_steps + 1):

            current_point = (j - 1) * max_value_of_independent_variable / number_of_steps

            arguments_vector = np.array(system_of_diff_equations.points[-1])

            k1 = system_of_diff_equations(current_point, arguments_vector)
            k2 = system_of_diff_equations(current_point + half_step_size,
                                          arguments_vector + half_step_size * k1)
            k3 = system_of_diff_equations(current_point + half_step_size,
                                          arguments_vector + half_step_size * k2)
            k4 = system_of_diff_equations(current_point + 2 * half_step_size,
                                          arguments_vector + 2 * half_step_size * k3)

            new_points = arguments_vector + max_value_of_independent_variable / \
                         number_of_steps / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

            system_of_diff_equations.points.append(new_points.tolist())

            if update_progress_signal is not None:
                update_progress_signal.emit(j)
    except FloatingPointError:
        raise OverflowError
