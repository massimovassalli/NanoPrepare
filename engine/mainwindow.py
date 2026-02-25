import sys
from PySide6.QtWidgets import QSpacerItem, QCheckBox, QTreeView,QGroupBox, QMainWindow, QVBoxLayout, QWidget, QPushButton, QComboBox, QHBoxLayout, QSlider, QLabel, QSizePolicy
from PySide6.QtCore import Qt
import pyqtgraph as pg

class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window title and geometry
        self.setWindowTitle("O11 Prepare")
        self.setGeometry(100, 100, 800, 600)
        self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
        # Create a central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Group 1: Button, QComboBox, and List
        group1_layout = QHBoxLayout()
        
        self.toggle_button = QPushButton("Optics11")
        self.toggle_button.setStyleSheet('color: green;')
        self.toggle_button.setCheckable(True)
        group1_layout.addWidget(self.toggle_button)
        self.openfile = QPushButton("Open files")
        self.openfolder = QPushButton("Open folder")
        self.limitOpen = QCheckBox("Limit to 100")
        self.limitOpen.setChecked(False)        
        self.nfiles = QLabel("0")
        group1_layout.addWidget(self.openfile)
        group1_layout.addWidget(self.openfolder)
        group1_layout.addWidget(self.limitOpen)
        group1_layout.addWidget(QLabel("Opened files: "))
        group1_layout.addWidget(self.nfiles)
        group1_layout.addWidget(QLabel('Segment:'))
        self.segmentSlider = QSlider(  )
        self.segmentSlider.setOrientation( Qt.Orientation.Horizontal )  # Vertical slider
        self.segmentSlider.setMinimum(0)
        self.segmentSlider.setMaximum(0)
        group1_layout.addWidget(self.segmentSlider)
        group1_layout.addItem( QSpacerItem(20, 20,  QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum) )
        self.timeview = QPushButton('Time view')
        self.tipselect = QPushButton('Set Tip')
        self.tipselect.setEnabled(False)
        self.save = QPushButton('Save')
        group1_layout.addWidget(self.timeview)
        group1_layout.addWidget(self.tipselect)
        group1_layout.addWidget(self.save)
        layout.addLayout(group1_layout)

        # Group 2: Horizontal Slider and two PyQtGraph PlotWidgets
        group2_layout = QHBoxLayout()
        self.slider = QSlider(  )
        self.slider.setMinimum(0)
        self.slider.setOrientation( Qt.Orientation.Vertical )  # Vertical slider
        self.graphleft = pg.PlotWidget()
        self.graphright = pg.PlotWidget()
        self.rightcurve = pg.PlotCurveItem([0,0],[0,0])
        self.graphright.addItem(self.rightcurve)
        group2_layout.addWidget(self.slider)
        group2_layout.addWidget(self.graphleft, stretch=1)
        group2_layout.addWidget(self.graphright, stretch=1)
        layout.addLayout(group2_layout)

        # Group 3: Button and Group of widgets
        group3 = QHBoxLayout()
        
        group3_left = QVBoxLayout()
        self.filelist = QTreeView()        
        
        #sub2_widget = QWidget()
        sub2_layout = QHBoxLayout()
        sub2_layout.addWidget(QLabel("Working dir: "))
        self.wdir = QLabel("./")
        sub2_layout.addWidget(self.wdir)
        sub2_layout.addItem(QSpacerItem(20, 20,  QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))       
        
        group3_left.addWidget(self.filelist)
        group3_left.addLayout(sub2_layout)
        
        left_widget = QWidget()
        left_widget.setLayout(group3_left)
        
        group3_right = QVBoxLayout()
        self.sel_screen = QComboBox()
        self.sel_screen.addItem('---select---')
        group3_right.addWidget(self.sel_screen)
        self.box_cp = QGroupBox()
        group3_right.addWidget(self.box_cp)
        
        right_widget = QWidget()
        right_widget.setLayout(group3_right)
        
        group3.addWidget(left_widget)
        group3.addWidget(right_widget)


        layout.addLayout(group3)