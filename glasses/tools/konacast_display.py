import sys

from PyQt5 import QtGui, QtWidgets, QtCore, QtNetwork, QtWebSockets

class ImageShower(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.server = QtWebSockets.QWebSocketServer("server", QtWebSockets.QWebSocketServer.NonSecureMode, self)
        self.sock = None

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)


        self.label = QtWidgets.QLabel()
            #label->setAlignment(Qt::AlignTop | Qt::AlignLeft);
        self.label.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.label.setScaledContents(True)
        self.label.setContentsMargins(0, 0, 0, 0)
        self.label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.label.setStyleSheet("QLabel { background-color: red }")

        layout.addWidget(self.label)
        #self.label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, .MinimumExpanding, QtCore.QSizePolicy.MinimumExpanding)
        #self.label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, .MinimumExpanding, QtCore.QSizePolicy.MinimumExpanding)

 #label->setSizePolicy(QSizePolicy::MinimumExpanding,
 #                             QSizePolicy::MinimumExpanding);
        #self.img = QtWidgets.QGraphicsView(self)
        #self.pixmapitem = None

        self.resize(320, 320)
        #self.img.setGeometry(QtCore.QRect(0, 0, 300, 300))

        if self.server.listen(QtNetwork.QHostAddress.Any, 8002):
            self.server.newConnection.connect(self.on_new_connection)



    def on_new_connection(self):
        print("Connected")
        sock = self.server.nextPendingConnection()

        self.sock = sock
        sock.setParent(self)
        sock.textMessageReceived.connect(self.on_text_message)
        sock.binaryMessageReceived.connect(self.on_binary_message)
        sock.disconnected.connect(self.on_disconnect)


    def on_text_message(self, msg):
        print("Got text: ", msg)


    def on_binary_message(self, msg):
        print("Got binary: ", len(msg))
        if len(msg) > 0:
            self.set_image(msg[4:])
            self.sock.sendTextMessage("1")

        #with open(f'images/image_{self.onind}.jpg', 'wb') as fout:
        #    fout.write(msg[4:])


    def on_disconnect(self):
        print("Disconnected")


    def set_image(self, data):
        pm = QtGui.QPixmap()
        pm.loadFromData(data)

        w = self.width()
        h = self.height()

        #// set a scaled pixmap to a w x h window keeping its aspect ratio
        #label->setPixmap(p.scaled(w,h,Qt::KeepAspectRatio));
        self.label.setPixmap(pm.scaled(w, h, QtCore.Qt.KeepAspectRatio))
#        if self.pixmapitem is None:
#            self.pixmapitem = QtWidgets.QGraphicsPixmapItem(pm)
#            scene = QtWidgets.QGraphicsScene(self)
#            scene.addItem(self.pixmapitem)
#
#            self.img.setScene(scene)
#        else:
#            self.pixmapitem.setPixmap(pm)
#
#
        #pm = QtGui.QPixmap.loadFromData(data)
        #self.label.setPixmap(pm)



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = ImageShower()
    win.show()

    sys.exit(app.exec_())
