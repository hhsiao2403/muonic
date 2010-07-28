from PyQt4 import QtGui
from PyQt4 import QtCore

from gui.LineEdit import LineEdit
from gui.PeriodicCallDialog import PeriodicCallDialog
from gui.ThresholdDialog import ThresholdDialog
from gui.HelpWindow import HelpWindow
from gui.live.ScalarsWindow import ScalarsWindow

tr = QtCore.QCoreApplication.translate
_NAME = 'muonic'



class MainWindow(QtGui.QMainWindow):
    
    def __init__(self, inqueue, outqueue, endcommand, win_parent = None):
        QtGui.QMainWindow.__init__(self, win_parent)
        self.resize(640, 480)
        self.setWindowTitle(_NAME)
        self.statusBar().showMessage(tr('MainWindow','Ready'))
        
        self.write_file = False
        self.inqueue = inqueue
        self.outqueue = outqueue
        self.endcommand = endcommand
        self.create_widgets()

    def create_widgets(self):
        self.label = QtGui.QLabel(tr('MainWindow','Command'))
        self.hello_edit = LineEdit()
        self.hello_button = QtGui.QPushButton(tr('MainWindow','Send'))
        self.file_button = QtGui.QPushButton(tr('MainWindow', 'Save to File'))
        self.periodic_button = QtGui.QPushButton(tr('MainWindow', 'Periodic Call'))

        QtCore.QObject.connect(self.hello_button,
                              QtCore.SIGNAL("clicked()"),
                              self.on_hello_clicked
                              )
        QtCore.QObject.connect(self.hello_edit,
                              QtCore.SIGNAL("returnPressed()"),
                              self.on_hello_clicked
                              )
        
        QtCore.QObject.connect(self.file_button,
                                QtCore.SIGNAL("clicked()"),
                                self.on_file_clicked
                                )
        QtCore.QObject.connect(self.periodic_button,
                                QtCore.SIGNAL("clicked()"),
                                self.on_periodic_clicked
                                )

        self.text_box = QtGui.QPlainTextEdit()
        self.text_box.setReadOnly(True)
        # only 500 lines history
        self.text_box.document().setMaximumBlockCount(500)
        v_box = QtGui.QVBoxLayout()
        v_box.addWidget(self.text_box)
        second_widget = QtGui.QWidget()
        h_box = QtGui.QHBoxLayout()
        h_box.addWidget(self.label)
        h_box.addWidget(self.hello_edit)
        h_box.addWidget(self.hello_button)
        h_box.addWidget(self.file_button)
        h_box.addWidget(self.periodic_button)
        second_widget.setLayout(h_box)
        v_box.addWidget(second_widget)
        central_widget = QtGui.QWidget()
        central_widget.setLayout(v_box)
        self.setCentralWidget(central_widget)
        
        exit = QtGui.QAction(QtGui.QIcon('/usr/share/icons/gnome/24x24/actions/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip(tr('MainWindow','Exit application'))
        self.connect(exit, QtCore.SIGNAL('triggered()'), QtCore.SLOT('close()'))
        thresholds = QtGui.QAction(QtGui.QIcon(''),'Thresholds', self)
        thresholds.setStatusTip(tr('MainWindow','Set trigger thresholds'))
        self.connect(thresholds, QtCore.SIGNAL('triggered()'), self.threshold_menu)
        helpdaqcommands = QtGui.QAction(QtGui.QIcon('icons/blah.png'),'DAQ Commands', self)
        self.connect(helpdaqcommands, QtCore.SIGNAL('triggered()'), self.help_menu)
        #liveanalysis = 
        scalars = QtGui.QAction(QtGui.QIcon('icons/blah.png'),'Scalars', self)
        self.connect(scalars, QtCore.SIGNAL('triggered()'), self.scalars_menu)
        menubar = self.menuBar()
        file = menubar.addMenu(tr('MainWindow','&File'))
        file.addAction(exit)
        settings = menubar.addMenu(tr('MainWindow', '&Settings'))
        settings.addAction(thresholds)
        help = menubar.addMenu(tr('MainWindow','&Help'))
        help.addAction(helpdaqcommands)
        liveanalysis = menubar.addMenu(tr('MainWindow','&Live Analysis'))
        liveanalysis.addAction(scalars)

        toolbar = self.addToolBar(tr('MainWindow','Exit'))
        toolbar.addAction(exit)

    def on_hello_clicked(self):
#        QtGui.QMessageBox.information(self,
#                                     "Hello",
#                                     "Hello %s"%self.hello_edit.displayText(),
#                                     QtGui.QMessageBox.Ok)
#        self.text_box.append(self.hello_edit.displayText())
        text = str(self.hello_edit.displayText())
        if len(text) > 0:
            self.outqueue.put(str(self.hello_edit.displayText()))
            self.hello_edit.add_hist_item(text)
        self.hello_edit.clear()

    def on_file_clicked(self):
        filename = QtGui.QFileDialog.getOpenFileName(self,
                                tr('MainWindow','Open output file'),
                                os.getenv('HOME'), tr('MainWindow','Text Files (*.txt);;All Files (*)'));
        filename = str(filename)
        if len(filename) > 0:
            if filename.endswith('.gz'):
                self.outputfile = gzip.open(filename,'w')
            else:
                self.outputfile = open(filename,'w')
            self.write_file = True
            self.file_label = QtGui.QLabel(tr('MainWindow','Writing to %s'%filename))
            self.statusBar().addPermanentWidget(self.file_label)


    def on_periodic_clicked(self):
        periodic_window = PeriodicCallDialog()
        rv = periodic_window.exec_()
        if rv == 1:
            period = periodic_window.time_box.value() * 1000 #We need the period in milliseconds
            command = str(periodic_window.textbox.text())
            commands = command.split('+')
            def periodic_put():
                for c in commands:
                    self.outqueue.put(c)
            self.periodic_put = periodic_put
            self.timer = QtCore.QTimer()
            QtCore.QObject.connect(self.timer,
                               QtCore.SIGNAL("timeout()"),
                               self.periodic_put)
            self.periodic_put()
            self.timer.start(period)
            self.periodic_status_label = QtGui.QLabel(tr('MainWindow','%s every %s sec'%(command,period/1000)))
            self.statusBar().addPermanentWidget(self.periodic_status_label)
        else:
            try:
                self.timer.stop()
                self.statusBar().removeWidget(self.periodic_status_label)
            except AttributeError:
                pass

    def threshold_menu(self):
        threshold_window = ThresholdDialog()
        rv = threshold_window.exec_()
        if rv == 1:
            # Here we should set the thresholds
            thresh_ch0 = int(threshold_window.ch0_input.text())
            thresh_ch1 = int(threshold_window.ch1_input.text())
            thresh_ch2 = int(threshold_window.ch2_input.text())
            thresh_ch3 = int(threshold_window.ch3_input.text())
            self.outqueue.put('TL 0 ' + str(thresh_ch0))
            self.outqueue.put('TL 1 ' + str(thresh_ch1))
            self.outqueue.put('TL 2 ' + str(thresh_ch2))
            self.outqueue.put('TL 3 ' + str(thresh_ch3))
   
    def help_menu(self):
        help_window = HelpWindow()
	#rv = threshold_window.exec_()
	help_window.exec_()
	#tr.exec_()	

    def scalars_menu(self):
        
        def readout_daqscalars(inqueue,outqueue):
            outqueue.put("CD")
            outqueue.put("DS")
            _scalars = str(inqueue.get(0))
            outqueue.put("CE")
            return _scalars
        
        #self.outqueue.put("CD")
        self.outqueue.put("DS")
        scalars_window = ScalarsWindow(scalars)
        scalars_window.exec_()
    
    def processIncoming(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        
        global scalars

        while self.inqueue.qsize():
            try:
                msg = self.inqueue.get(0)
                # Check contents of message and do what it says
                # As a test, we simply print it
                # check for scalar information
                if msg[0]=='D' and msg[1] == 'S':
                    if len(msg) > 5:
                        scalars = msg
                self.text_box.appendPlainText(str(msg))
                if self.write_file:
                    self.outputfile.write(str(msg)+'\n')
            except Queue.Empty:
                pass
    
    def closeEvent(self, ev):
        """
        We just call the endcommand when the window is closed
        instead of presenting a button for that purpose.
        """
        if self.write_file:
            self.outputfile.close()
        self.endcommand()

# vim: ai ts=4 sts=4 et sw=4
