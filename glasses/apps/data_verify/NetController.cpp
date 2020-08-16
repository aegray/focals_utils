#include "NetController.h"

#include <QTimer>
#include <QCoreApplication>
#include <QAbstractSocket>

#include <stdlib.h>
#include <fstream>
#include <iostream>

#define NOSSL

NetController::NetController(QObject *parent) :
    QObject(parent)
{
    //connect(&socket_, &QAbstractSocket::connected, this, &NetController::onTcpConnected);
    



    connect(&socket_, SIGNAL(connected()), this, SLOT(onTcpConnected())); 
    connect(&socket_, SIGNAL(disconnected()), this, SLOT(onTcpDisconnected())); 
    connect(&socket_, SIGNAL(error(QAbstractSocket::SocketError)), this, SLOT(onTcpError(QAbstractSocket::SocketError)));
    connect(&socket_, SIGNAL(readyRead()), this, SLOT(onTcpReadyRead()));

        
    socket_.connectToHost("192.168.1.6", 4343); 
}



void NetController::onTcpConnected()
{
    std::cout << "Connected" << std::endl;
}

void NetController::onTcpReadyRead()
{
    auto data = socket_.readAll();

    // echo it back 
    socket_.write(data);
}

void NetController::onTcpDisconnected()
{
    std::cout << "Disconnected" << std::endl;
    QCoreApplication::quit();
}
    
void NetController::onTcpError(QAbstractSocket::SocketError socketError)
{
    std::cout << "Tcp error" << std::endl;
    QCoreApplication::quit();
}


