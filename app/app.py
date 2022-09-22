import sys
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, \
    QProgressBar, QPushButton, QComboBox
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from PyQt5.QtCore import QPointF, QTimer
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator

import numpy as np
import util
from math import *
from arch_equations import ArchEquationsSystem


class ArchApp(QWidget):
    """Class of the Qt app for modeling arch oscillations"""

    def __init__(self):
        super().__init__()
        self.chart = QChart()
        self.chart_view = QChartView(self.chart)
        self.create_ui()
        self.simulation_duration = 0
        self.eps = 0.02
        self.system = None
        self.solver_thread = None
        self.timer = QTimer()
        self.x_div = 0
        self.t_div = 0
        self.t_moment = 0
        self.initialize_ui()
        self.show()

    def create_ui(self):
        self.setWindowTitle("Arch oscillations")
        self.main_vertical = QVBoxLayout()

        # setting up a chart
        self.chart.createDefaultAxes()
        self.chart.setTitle("Flexure")
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)
        self.chart_view.setMinimumHeight(500)

        self.main_vertical.addWidget(self.chart_view)

        # input data container
        self.inp_layout = QHBoxLayout()

        # first column

        self.initial_flexure_label = QLabel("Initial flexure")
        self.initial_speed_label = QLabel("Initial speed")
        self.t_moment_label = QLabel("t = 0")

        self.initial_flexure_edit = QLineEdit()
        self.initial_speed_edit = QLineEdit()
        empty_label = QLabel("")

        self.vb11 = QVBoxLayout()
        self.vb11.addWidget(self.initial_flexure_label)
        self.vb11.addWidget(self.initial_speed_label)
        self.vb11.addWidget(self.t_moment_label)

        self.vb12 = QVBoxLayout()
        self.vb12.addWidget(self.initial_flexure_edit)
        self.vb12.addWidget(self.initial_speed_edit)
        self.vb12.addWidget(empty_label)

        # second column
        self.T_label = QLabel("Simulation duration")
        self.t_div_label = QLabel("Divisions by t [1/с]")
        self.x_div_label = QLabel("Divisions by х")

        self.vb21 = QVBoxLayout()
        self.vb21.addWidget(self.T_label)
        self.vb21.addWidget(self.t_div_label)
        self.vb21.addWidget(self.x_div_label)

        self.T_edit = QLineEdit()
        self.t_div_edit = QLineEdit()
        self.x_div_edit = QLineEdit()

        self.vb22 = QVBoxLayout()
        self.vb22.addWidget(self.T_edit)
        self.vb22.addWidget(self.t_div_edit)
        self.vb22.addWidget(self.x_div_edit)

        self.hb1 = QHBoxLayout()
        self.hb1.addLayout(self.vb11)
        self.hb1.addLayout(self.vb12)

        self.hb2 = QHBoxLayout()
        self.hb2.addLayout(self.vb21)
        self.hb2.addLayout(self.vb22)

        # adding columns to the input block
        self.inp_layout.addLayout(self.hb1)
        self.inp_layout.addLayout(self.hb2)

        # adding input block to main_Layout
        self.main_vertical.addLayout(self.inp_layout)

        # adding bottom layout
        self.bottom_layout = QHBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(1)
        self.progress_bar.setValue(0)
        self.calc_btn = QPushButton("Calculate")

        self.calc_btn.clicked.connect(self.calc_btn_clicked)
        self.play_btn = QPushButton("Start animation")
        self.play_btn.clicked.connect(self.play_btn_clicked)
        self.speed_combobox = QComboBox()
        self.speed_combobox.addItems(['×0.0625', '×0.125', "×0.25", '×0.5', '×1', '×1.5', '×2'])
        self.speed_combobox.setCurrentIndex(1)

        self.vb3 = QVBoxLayout()
        self.vb3.addWidget(self.progress_bar)


        self.bottom_layout.addLayout(self.vb3)
        self.vb4 = QVBoxLayout()
        self.vb4.addWidget(self.calc_btn)
        self.vb4.addWidget(self.speed_combobox)
        self.vb4.addWidget(self.play_btn)
        self.bottom_layout.addLayout(self.vb4)

        # validator
        self.int_validator = QIntValidator()
        self.int_validator.setBottom(1)
        self.int_validator.setTop(3000)
        self.T_edit.setValidator(self.int_validator)
        self.x_div_edit.setValidator(self.int_validator)
        self.t_div_edit.setValidator(self.int_validator)

        self.main_vertical.addLayout(self.bottom_layout)
        self.setLayout(self.main_vertical)

    def initialize_ui(self):
        self.T_edit.setText("5")
        self.x_div_edit.setText("150")
        self.t_div_edit.setText("500")
        self.initial_flexure_edit.setText("x")
        self.initial_speed_edit.setText("x")

        initial_flexure = np.sin(np.linspace(0, np.pi, 100))
        x_values = np.linspace(0, np.pi, 100)
        self.series = QLineSeries()
        self.series.setName("Flexure")
        for i in range(100):
            self.series.append(QPointF(x_values[i], initial_flexure[i]))
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        self.chart.axisY().setMax(3)
        self.chart.axisY().setMin(-3)

    def calc_btn_clicked(self):
        """Handles click on "Calculate" button"""

        if not self.calculation_params_correct():
            return

        self.simulation_duration = int(self.T_edit.text())
        self.t_div = int(self.t_div_edit.text()) * self.simulation_duration
        self.x_div = int(self.x_div_edit.text())

        self.progress_bar.setMaximum(self.t_div)

        flexure_code = self.initial_flexure_edit.text()
        speed_code = self.initial_speed_edit.text()

        if not util.check_initial_conditions(flexure_code, speed_code):
            self.t_moment_label.setText("Check the initial conditions")
            return

        try:
            initial_flexure = []
            initial_speed = []
            for i in range(self.x_div):
                x = (i + 1) * pi/(self.x_div + 1)
                if eval(flexure_code) is None or not type(eval(flexure_code)) == int and not type(eval(flexure_code)) == float:
                    self.t_moment_label.setText("Check the initial conditions")
                    return
                if eval(speed_code) is None or not type(eval(speed_code)) == int and not type(eval(speed_code)) == float:
                    self.t_moment_label.setText("Check the initial conditions")
                    return

                initial_flexure.append(eval(flexure_code))
                initial_speed.append(eval(speed_code))

                self.system = ArchEquationsSystem(self.x_div, initial_flexure, initial_speed, self.eps)

        except Exception:
            self.t_moment_label.setText("Check the initial conditions")
            return
        try:
            self.run_calculation()
        except OverflowError:
            self.t_moment_label.setText("Decline the step by time")
            return None

    def run_calculation(self):
        self.timer.stop()
        if self.solver_thread is not None:
            self.solver_thread.terminate()
        self.solver_thread = util.SolverThread(self.system, self.simulation_duration, self.t_div, self.update_progress, self.handle_overflow)
        self.solver_thread.start()

    def handle_overflow(self):
        """Handles OverflowError appearing during solution of the system"""

        self.t_moment_label.setText("Decline the step by time")
        self.system = None
        self.solver_thread.terminate()

    def play_btn_clicked(self):
        if self.system is not None and len(self.system.points) > 1 and self.solver_thread.isFinished():
            self.begin_animation()

    def begin_animation(self):
        self.chart.axisY().setMax(max(0,np.array(self.system.points)[:, :self.x_div].max()))
        self.chart.axisY().setMin(min(0,np.array(self.system.points)[:, :self.x_div].min()))
        self.speed_multiplier = float(self.speed_combobox.currentText()[1:])
        self.t_moment = 0
        self.timer = QTimer()
        self.timer.setInterval(int(1000 * self.simulation_duration / self.t_div / self.speed_multiplier))
        self.timer.timeout.connect(self.redraw_chart)
        self.timer.start()

    def update_progress(self, i):
        self.progress_bar.setValue(i)

    def redraw_chart(self):
        points = [QPointF(0, 0)]
        i = 0
        for y in self.system.points[self.t_moment][:self.x_div]:
            points.append(QPointF((i+1)/(self.x_div+1)*np.pi, y))
            i += 1
        points.append(QPointF(np.pi, 0))
        self.series.replace(points)
        self.t_moment += 1
        self.chart_view.update()
        self.t_moment_label.setText("t = " + str(trunc(self.t_moment / self.t_div * self.simulation_duration)))
        if self.t_moment == self.t_div:
            self.timer.stop()

    def calculation_params_correct(self):
        if self.int_validator.validate(self.T_edit.text(), 0)[0] == 2 \
                and self.int_validator.validate(self.x_div_edit.text(), 0)[0] == 2 \
                and self.int_validator.validate(self.t_div_edit.text(), 0)[0] == 2 \
                and not self.x_div_edit.text() == "1" \
                and not int(self.x_div_edit.text()) > 300:
            return True
        self.t_moment_label.setText("Check the solution settings")
        return False


App = QApplication(sys.argv)
window = ArchApp()
sys.exit(App.exec_())
