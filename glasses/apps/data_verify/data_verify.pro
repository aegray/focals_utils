TEMPLATE = app

QT += core network

QMAKE_CXXFLAGS += -std=c++0x 

SOURCES += NetController.cpp main.cpp 

HEADERS += NetController.h

#quick qml

#RESOURCES += \
#    text.qrc \
#    ../shared/shared.qrc

#target.path = $$[QT_INSTALL_EXAMPLES]/quick/text
#INSTALLS += target
