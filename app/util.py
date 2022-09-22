import parser
import re
from PyQt5.QtCore import QThread, pyqtSignal
from differential_equations_solver.runge_kutta import runge_kutta_4


class SolverThread(QThread):
    """Class solving the system of differential equations in a separate thread"""

    updateProgress = pyqtSignal(int)
    overflowSignal = pyqtSignal()

    def __init__(self, system, duration, num_divisions, update_progress, handle_overflow):
        super().__init__()
        self.system = system
        self.duration = duration
        self.num_divisions = num_divisions
        self.updateProgress.connect(update_progress)
        self.overflowSignal.connect(handle_overflow)

    def run(self):
        try:
            runge_kutta_4(self.system,
                          self.duration,
                          self.num_divisions,
                          self.updateProgress)
        except OverflowError:
            self.overflowSignal.emit()


def check_initial_conditions(initial_flexure, initial_speed):
    """Checks if input code contains only allowed operators and can be compiled"""

    allowed_elements = [
        '[.]', ' ', 'x', 'pi', 'e', 'cos', 'sin', '[+]', '-', '[*]', '/', '\d', '[(]', '[)]'
    ]
    flex = initial_flexure
    speed = initial_speed
    for element in allowed_elements:
        flex = re.sub(element, '', flex)
        speed = re.sub(element, '', speed)
    if not (flex == '' or speed == ''):
        return False

    try:
        parser.expr(initial_flexure).compile()
        parser.expr(initial_speed).compile()
    except Exception:
        return False
    return True
