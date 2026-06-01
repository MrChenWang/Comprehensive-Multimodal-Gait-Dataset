import os
from tqdm import tqdm
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os.path as osp
import csv
import math
import numpy as np
import config
from concurrent.futures import ThreadPoolExecutor
import pyqtgraph as pg
import traceback

class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super(Ui_MainWindow, self).__init__()
        # root path
        self.root_path = 'G:\\ExoDataCollect\\Data_public3'
        self.files = []
        for file in os.listdir(self.root_path):
            self.files.append(file)
        # define lists
        self.time_lst = []
        self.frame_lst_Lleg, self.frame_lst_Mhip, self.frame_lst_Rleg = [], [], []
        self.lower_limb_status, self.Foot_pressure_values = [], []
        self.gait_phases, self.annotations, self.COP_data = [], [], []
        self.total_lst = [self.frame_lst_Lleg, self.frame_lst_Mhip, self.frame_lst_Rleg,
                          self.lower_limb_status, self.Foot_pressure_values,
                          self.gait_phases, self.annotations, self.COP_data]
        self.angle_curve = [[] for _ in range(7)]
        self.velocity_curve = [[] for _ in range(7)]
        self.x_value = [float(i) / 50 for i in range(100)]
        # Timer initialization
        self.timer = QtCore.QTimer()
        self.interval_ms = 10
        self.read_index = 0
        # Image Format
        self.img_format = ".jpg"
        # Present Frame
        self.M_hip_img = None
        self.fp_vis_img = None
        self.angle_vis_img = None
        # System Status
        self.sys_active = False
        self.area = config.area
        self.limit = 5000
        self.backimg_l = cv2.imread('materials\\left_foot.jpg')
        self.backimg_r = cv2.imread('materials\\right_foot.jpg')
        self.window_size = (1920, 1080)
        # Control appearance
        self.colors = ['blue', 'red', 'yellow', 'white', 'purple', 'pink', 'cyan']
        self.legends = ['L_hip', 'R_hip', 'L_knee',	'R_knee', 'L_ankle', 'R_ankle',	'M_hip']
        self.button_color = "color: rgb(255, 255, 255);border-color: rgb(0, 0, 0);background-color: rgb(50,50,237);"
        self.button_style = """
                    QPushButton {
                        border: none;      
                        background: transparent;  
                    }
                    QPushButton:hover {
                        opacity: 0.9;
                    }
                    QPushButton:pressed {
                        opacity: 0.8;
                    }
                """

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(self.window_size[0], self.window_size[1])
        MainWindow.setAcceptDrops(True)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet("background-color: rgb(240, 248, 255);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Define labels
        self.label_show_camera_Lleg = self.define_label((0, 0), (640, 360))
        self.label_show_camera_Mhip = self.define_label((640, 0), (640, 360))
        self.label_show_camera_Rleg = self.define_label((1280, 0), (640, 360))
        self.label_show_fp = self.define_label((0, 360), (500, 624))
        self.label_show_angle = self.define_label((500, 360), (624, 624))
        self.label_show_frame = self.define_label((1200, 1000), (350, 50), "font-size:25px; background-color: rgb(240, 248, 255);")
        self.label_show_legend = self.define_label((1124, 960), (96, 24), "background-color: rgb(0,0,0);color:white;")
        self.label_show_legend.setText("Legend:")
        self.label_show_legends = [self.define_label((1124 + 96 + 100 * i, 960), (100, 24), "font-size:20px;background-color: rgb(0,0,0);color:" + self.colors[i] + ";") for i in range(7)]
        for i in range(7):
            self.label_show_legends[i].setText("—" + self.legends[i])
        self.label_participant = self.define_label((50, 1000), (150, 50), "font-size:25px;background-color: rgb(240, 248, 255);")
        self.label_participant.setText("Participant:")
        self.label_scene = self.define_label((400, 1000), (100, 50), "font-size:25px;background-color: rgb(240, 248, 255);")
        self.label_scene.setText("Scene:")

        # Define buttons
        self.button_open_camera = self.define_button((930, 1000), (60, 60), Icon_path="materials\\start.png")
        self.one_frame_forward = self.define_button((1030, 1000), (60, 60), Icon_path="materials\\forward.png")
        self.one_frame_backward = self.define_button((830, 1000), (60, 60), Icon_path="materials\\backward.png")

        # Define combo boxes
        self.combo_file_choose = QtWidgets.QComboBox(self.centralwidget)
        self.combo_file_choose.setGeometry(QtCore.QRect(220, 1000, 150, 50))
        self.combo_file_choose.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        self.combo_file_choose.addItems(['None'] + self.files)

        self.combo_file_choose1 = QtWidgets.QComboBox(self.centralwidget)
        self.combo_file_choose1.setGeometry(QtCore.QRect(500, 1000, 300, 50))
        self.combo_file_choose1.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))

        # Define plot controls
        self.pens_angle = self.define_plot((-90, 90), 'Angle', 'deg', (1124, 360), (796, 200))
        self.pens_velocity = self.define_plot((-600, 600), 'Gyro', 'deg/s', (1124, 560), (796, 400))

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Visualization Tool for Comprehensive Multimodal Gait Dataset"))
        self.button_open_camera.setText(_translate("MainWindow", ""))

    def slot_init(self):  # Build connection
        self.button_open_camera.clicked.connect(self.button_open_camera_click)
        self.one_frame_forward.clicked.connect(self.one_frame_forward_click)
        self.one_frame_backward.clicked.connect(self.one_frame_backward_click)
        self.combo_file_choose.currentIndexChanged.connect(self.on_imu_port_changed)
        self.combo_file_choose1.currentIndexChanged.connect(self.on_imu_port_changed1)
        self.timer.timeout.connect(self.main_loop)

    def define_plot(self, y_range, y_name, y_unit, loc, size):
        plt = pg.PlotWidget(self.centralwidget)
        plt.setGeometry(QtCore.QRect(loc[0], loc[1], size[0], size[1]))
        plt.setStyleSheet("background-color: rgb(255, 255, 255);")
        plt.setLabel('left', y_name, units=y_unit)
        plt.setLabel('bottom', 'Time', units='s')
        plt.setXRange(0, 2)
        plt.setYRange(y_range[0], y_range[1])
        Pens = [plt.plot() for _ in range(7)]
        for i in range(7):
            Pens[i].setPen(self.colors[i])
        return Pens

    def define_label(self, loc, size, bk_color="background-color: rgb(255,255,255);"):
        label = QtWidgets.QLabel(self.centralwidget)
        label.setGeometry(QtCore.QRect(loc[0], loc[1], size[0], size[1]))
        label.setStyleSheet(bk_color)
        label.setScaledContents(True)
        return label

    def define_button(self, loc, size, Icon_path=None):
        button = QtWidgets.QPushButton(self.centralwidget)
        if Icon_path != None:
            button.setIcon((QIcon(Icon_path)))
        button.setGeometry(QtCore.QRect(loc[0], loc[1], size[0], size[1]))
        button.setStyleSheet(self.button_style)
        button.setFlat(False)
        return button

    def button_open_camera_click(self):
        if len(self.time_lst) > 0:
            if not self.sys_active:
                self.timer.start(self.interval_ms)
                self.sys_active = True
                self.button_open_camera.setIcon(QtGui.QIcon("materials\\pause.png"))
            else:
                self.sys_active = False
                self.button_open_camera.setIcon(QtGui.QIcon("materials\\start.png"))
                self.timer.stop()
        else:
            print("Please select a valid folder first!")

    def one_frame_forward_click(self):
        if self.read_index < len(self.time_lst) - 1:
            self.main_loop()

    def one_frame_backward_click(self):
        if self.read_index > 1:
            self.read_index -= 2
            self.main_loop()

    def on_imu_port_changed(self):
        self.clear_cache()
        self.combo_file_choose1.clear()
        sub_files = []
        current_file = osp.join(self.root_path, self.combo_file_choose.currentText())
        for file in os.listdir(current_file):
            sub_files.append(file)
        self.combo_file_choose1.addItems(['None'] + sub_files)

    def clear_cache(self):
        for lst in self.total_lst:
            lst.clear()
        for i in range(7):
            self.angle_curve[i].clear()
            self.velocity_curve[i].clear()
        self.read_index = 0
        if self.sys_active:
            self.sys_active = False
            self.timer.stop()
            self.button_open_camera.setIcon(QtGui.QIcon("materials\\start.png"))

    def on_imu_port_changed1(self):
        if self.combo_file_choose1.currentText() != "None" and self.combo_file_choose1.count() > 0:
            self.clear_cache()
            # Load data from the specified folder
            path = osp.join(self.root_path, self.combo_file_choose.currentText(), self.combo_file_choose1.currentText())
            print("Selected:  " + path)
            # Read IMU data
            self.time_lst, self.lower_limb_status = self.read_csv(path, "IMU_angle.csv")
            _, velocity_values = self.read_csv(path, "IMU_gyro.csv")
            # Read Foot pressure
            _, self.Foot_pressure_values = self.read_csv(path, "Foot_pressure.csv")
            # Read Annotations
            _, self.annotations = self.read_csv(path, "Annotations.csv")
            # Extract gait phases
            self.gait_phases = [[item[-4], item[-2]] for item in self.annotations]
            # Read COP
            _, self.COP_data = self.read_csv(path, "Center_of_pressure.csv")
            # Prepare data for curves
            for i in range(7):
                self.angle_curve[i] = [0.0] * 100 + self.angle_curve[i]
                self.velocity_curve[i] = [0.0] * 100 + self.velocity_curve[i]
                for j in range(len(self.time_lst)):
                    self.angle_curve[i].append(eval(self.lower_limb_status[j][i]))
                    self.velocity_curve[i].append(eval(velocity_values[j][i]))
            # Read 3-channel frame sequences
            camera_configs = [
                ("L_leg", self.frame_lst_Lleg),
                ("R_leg", self.frame_lst_Rleg),
                ("M_hip", self.frame_lst_Mhip)
            ]
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(self.read_photos, path, loc): lst
                    for loc, lst in camera_configs
                }
                for future in futures:
                    lst = futures[future]
                    lst.extend(future.result())
            # Run main loop once to show view
            self.main_loop()

    def read_csv(self, path, file):
        file_total_path = osp.join(path, file)
        time_lst = []
        data_lst = []
        if osp.exists(file_total_path):
            with open(file_total_path, 'r', newline='') as f:
                csv_reader = csv.reader(f)
                header = next(csv_reader)
                print(header)
                for row in csv_reader:
                    time_lst.append(row[0])
                    data_lst.append(row[1:])
        return time_lst, data_lst

    def read_photos(self, path, loc):
        img_root = osp.join(path, loc)

        def process_single_image(img_name):
            img_path = osp.join(img_root, img_name + self.img_format)
            img = cv2.imread(img_path)
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        lst = [None] * len(self.time_lst)
        with tqdm(total=len(self.time_lst), desc="Reading images from:" + loc) as pbar:
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = {
                    executor.submit(process_single_image, img_name): idx
                    for idx, img_name in enumerate(self.time_lst)
                }

                for future in futures:
                    idx = futures[future]
                    lst[idx] = future.result()
                    pbar.update(1)
        return lst

    def main_loop(self):
        try:
            for j in range(7):
                self.pens_angle[j].setData(self.x_value, self.angle_curve[j][self.read_index: self.read_index + 100])
                self.pens_velocity[j].setData(self.x_value, self.velocity_curve[j][self.read_index: self.read_index + 100])
            # Generate stick man
            lower_limb_status = self.lower_limb_status[self.read_index]
            angle_vis = self.vis_lower_limb_status(lower_limb_status)
            # Generate heatmap for foot pressure
            left_fp = self.vis_FP_pressure(self.Foot_pressure_values[self.read_index][:48], is_left=True)
            right_fp = self.vis_FP_pressure(self.Foot_pressure_values[self.read_index][48:], is_left=False)
            if len(self.COP_data) != 0:
                if float(self.COP_data[self.read_index][0]) * float(self.COP_data[self.read_index][1]) != 0:
                    L_COP_x = int(float(self.COP_data[self.read_index][0]) * 202.5) + 115
                    L_COP_y = 610 - int(float(self.COP_data[self.read_index][1]) * 599)
                    cv2.circle(left_fp, (L_COP_x, L_COP_y), 5, (255, 255, 255), 5)
                if float(self.COP_data[self.read_index][2]) * float(self.COP_data[self.read_index][3]) != 0:
                    R_COP_x = 135 - int(float(self.COP_data[self.read_index][2]) * 202.5)
                    R_COP_y = 610 - int(float(self.COP_data[self.read_index][3]) * 599)
                    cv2.circle(right_fp, (R_COP_x, R_COP_y), 5, (255, 255, 255), 5)
            fp_vis = np.hstack((left_fp, right_fp))
            fp_vis_rgb = cv2.cvtColor(fp_vis, cv2.COLOR_BGR2RGB)
            L_leg_img = self.frame_lst_Lleg[self.read_index]
            R_leg_img = self.frame_lst_Rleg[self.read_index]
            M_hip_img = self.frame_lst_Mhip[self.read_index]
            cv2.putText(L_leg_img, "Left_camera", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(M_hip_img, "Middle_camera", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(R_leg_img, "Right_camera", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2, cv2.LINE_AA)
            show_camera_img_Lleg = QtGui.QImage(L_leg_img.data, L_leg_img.shape[1], L_leg_img.shape[0],
                                                QtGui.QImage.Format_RGB888)
            show_camera_img_Rleg = QtGui.QImage(R_leg_img.data, R_leg_img.shape[1], R_leg_img.shape[0],
                                                QtGui.QImage.Format_RGB888)
            show_camera_img_Mhip = QtGui.QImage(M_hip_img.data, M_hip_img.shape[1], M_hip_img.shape[0],
                                                QtGui.QImage.Format_RGB888)
            self.label_show_camera_Lleg.setPixmap(QtGui.QPixmap.fromImage(show_camera_img_Lleg))
            self.label_show_camera_Rleg.setPixmap(QtGui.QPixmap.fromImage(show_camera_img_Rleg))
            self.label_show_camera_Mhip.setPixmap(QtGui.QPixmap.fromImage(show_camera_img_Mhip))
            show_fp_img = QtGui.QImage(fp_vis_rgb.data, fp_vis_rgb.shape[1], fp_vis_rgb.shape[0],
                                       QtGui.QImage.Format_RGB888)
            self.label_show_fp.setPixmap(QtGui.QPixmap.fromImage(show_fp_img))
            show_angle_img = QtGui.QImage(angle_vis.data, angle_vis.shape[1], angle_vis.shape[0],
                                          QtGui.QImage.Format_RGB888)
            self.label_show_angle.setPixmap(QtGui.QPixmap.fromImage(show_angle_img))
            self.M_hip_img = cv2.cvtColor(M_hip_img, cv2.COLOR_BGR2RGB)
            self.fp_vis_img = cv2.cvtColor(fp_vis_rgb, cv2.COLOR_BGR2RGB)
            self.angle_vis_img = cv2.cvtColor(angle_vis, cv2.COLOR_BGR2RGB)
            self.read_index += 1
            self.label_show_frame.setText("Current frame: " + str(self.read_index) + "/" + str(len(self.time_lst)))
            if self.read_index == len(self.time_lst):
                self.read_index = 0
                self.sys_active = False
                self.button_open_camera.setIcon(QtGui.QIcon("materials\\start.png"))
                self.timer.stop()
        except Exception as e:
            print(f"Exception type: {type(e).__name__}")
            print(f"Exception description：{str(e)}")
            print("Exception stack:")
            traceback.print_exc()

    def vis_FP_pressure(self, half_data, is_left):
        canvas = np.zeros((78, 31, 3), dtype="uint8")
        for i in range(48):
            if int(half_data[i]) > 0:
                if is_left:
                    canvas = self.heatmap_circle(canvas, (self.area[i][1] // 32, self.area[i][0] // 32),
                                                 int(half_data[i]))
                else:
                    canvas = self.heatmap_circle(canvas, (self.area[i][1] // 32, 31 - self.area[i][0] // 32),
                                                 int(half_data[i]))
        canvas = cv2.resize(canvas, (250, 624))
        if is_left:
            return cv2.add(self.backimg_l, canvas)
        else:
            return cv2.add(self.backimg_r, canvas)

    def heatmap_circle(self, canvas, point, value, radius=5):
        for i in range(point[0] - radius, point[0] + radius):
            for j in range(point[1] - radius, point[1] + radius):
                dis = math.sqrt((i - point[0]) ** 2 + (j - point[1]) ** 2)
                if dis <= radius and 0 <= i < 77 and 0 <= j < 31:
                    temp = value / self.limit * (1 - dis / radius) if value < self.limit else 1 - dis / radius
                    temp = int(temp * 255)
                    canvas[i, j, 0] = np.clip(float(canvas[i, j, 0]) + temp, 0, 255)
        return canvas

    def vis_lower_limb_status(self, lower_limb_status):
        p_o = (320, 200)
        torso, big_leg, small_leg, foot = 100, 150, 120, 50
        canvas = np.ones((600, 640, 3), dtype="uint8") * 255
        L_hip, R_hip, L_knee, R_knee, L_ankle, R_ankle, M_hip = [math.radians(eval(item)) for item in lower_limb_status]
        # IMU angle refers to the angle relative to the vertical direction
        p_M_h = (p_o[0] - int(torso * math.sin(M_hip)), p_o[1] - int(torso * math.cos(M_hip)))
        p_L_h = (p_o[0] - int(big_leg * math.sin(L_hip)), p_o[1] + int(big_leg * math.cos(L_hip)))
        p_R_h = (p_o[0] - int(big_leg * math.sin(R_hip)), p_o[1] + int(big_leg * math.cos(R_hip)))
        p_L_k = (p_L_h[0] - int(small_leg * math.sin(L_knee)), p_L_h[1] + int(small_leg * math.cos(L_knee)))
        p_R_k = (p_R_h[0] - int(small_leg * math.sin(R_knee)), p_R_h[1] + int(small_leg * math.cos(R_knee)))
        p_L_a = (p_L_k[0] + int(foot * math.cos(L_ankle)), p_L_k[1] - int(foot * math.sin(L_ankle)))
        p_R_a = (p_R_k[0] + int(foot * math.cos(R_ankle)), p_R_k[1] + int(foot * math.sin(R_ankle)))
        cv2.arrowedLine(canvas, (400, 30), (600, 30), (0, 0, 0), thickness=2, line_type=8, shift=0, tipLength=0.1)
        cv2.putText(canvas, "Forward Direction", (400, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.line(canvas, p_o, p_M_h, (0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
        cv2.line(canvas, p_o, p_L_h, (0, 0, 255), thickness=2, lineType=cv2.LINE_AA)
        cv2.line(canvas, p_o, p_R_h, (255, 0, 0), thickness=2, lineType=cv2.LINE_AA)
        cv2.line(canvas, p_L_h, p_L_k, (0, 0, 255), thickness=2, lineType=cv2.LINE_AA)
        cv2.line(canvas, p_R_h, p_R_k, (255, 0, 0), thickness=2, lineType=cv2.LINE_AA)
        cv2.line(canvas, p_L_k, p_L_a, (0, 0, 255), thickness=2, lineType=cv2.LINE_AA)
        cv2.line(canvas, p_R_k, p_R_a, (255, 0, 0), thickness=2, lineType=cv2.LINE_AA)
        for x in range(20, 640, 20):
            cv2.line(canvas, (x, p_o[1] + 270), (x + 10, p_o[1] + 270), (0, 0, 0), thickness=2, lineType=cv2.LINE_AA)

        if len(self.gait_phases) != 0:
            cv2.circle(canvas, (p_L_k[0], p_L_k[1] + 20), 8,
                       (0, 0, 255) if int(self.gait_phases[self.read_index][0]) == 1 else (255, 255, 0), thickness=-1)
            cv2.circle(canvas, (p_R_k[0], p_R_k[1] + 20), 8,
                       (255, 0, 0) if int(self.gait_phases[self.read_index][1]) == 1 else (255, 255, 0), thickness=-1)
        if len(self.annotations) != 0:
            gait_idx = self.annotations[self.read_index][0:16].index("1")
            cv2.putText(canvas, "Current status: " + config.public_header[gait_idx + 1], (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1,
                        cv2.LINE_AA)
        cv2.putText(canvas, "Legend:", (20, 530), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.circle(canvas, (130, 520), 8, (0, 0, 255) , thickness=-1)
        cv2.putText(canvas, "Left stance phase", (150, 530), cv2.FONT_HERSHEY_SIMPLEX,0.7, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.circle(canvas, (130, 550), 8, (255, 0, 0) , thickness=-1)
        cv2.putText(canvas, "Right stance phase", (150, 560), cv2.FONT_HERSHEY_SIMPLEX,0.7, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.circle(canvas, (130, 580), 8, (255, 255, 0) , thickness=-1)
        cv2.putText(canvas, "Swing phase", (150, 590), cv2.FONT_HERSHEY_SIMPLEX,0.7, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.line(canvas, (420, 520), (480, 520), (0, 0, 255), thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(canvas, "Left leg", (500, 530), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.line(canvas, (420, 550), (480, 550), (255, 0, 0), thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(canvas, "Right leg", (500, 560), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.line(canvas, (420, 580), (480, 580), (0, 0, 0), thickness=2, lineType=cv2.LINE_AA)
        cv2.putText(canvas, "Torso", (500, 590), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 1, cv2.LINE_AA)
        return canvas


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainWindow)
    ui.slot_init()
    mainWindow.show()
    sys.exit(app.exec_())