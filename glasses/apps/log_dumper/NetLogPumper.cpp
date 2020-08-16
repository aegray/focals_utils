#include "NetLogPumper.h"

#include <QTimer>
#include <QCoreApplication>
#include <QAbstractSocket>

#include <stdlib.h>
#include <fstream>
#include <iostream>

#define NOSSL

NetLogPumper::NetLogPumper(QObject *parent) :
    QObject(parent)
{
    //connect(&file_watcher_, SIGNAL(fileChanged(const QString &path)), this, SLOT(onFileChanged(const QString &path)));

    //file_watcher_.addPath("/data/app/applog.txt");

    connect(&timer_, SIGNAL(timeout()), this, SLOT(onTimer()));
    //    });
    //        [this](const QString& path){
    //    Q_UNUSED(path)
    //    m_engine->clearComponentCache();
    //    emit filePathChanged();
    //});
    connect(&socket_, SIGNAL(connected()), this, SLOT(onTcpConnected())); 
    connect(&socket_, SIGNAL(disconnected()), this, SLOT(onTcpDisconnected())); 
    connect(&socket_, SIGNAL(error(QAbstractSocket::SocketError)), this, SLOT(onTcpError(QAbstractSocket::SocketError)));
    //connect(&socket_, SIGNAL(readyRead()), this, SLOT(onTcpReadyRead()));
    //
    timer_.start(1000);
}


void NetLogPumper::onTimer()
{
    if (connected_)
    {
        QFile file("/data/app/applog.txt");
        if(!file.open(QIODevice::ReadOnly)) {
            prev_off_ = 0;
            prev_size_ = 0;
            needs_pub_ = false;
            return;
        }

        int cursz = file.size();
        if (cursz == prev_size_) {
            file.close();
            return;
        }

        if (cursz < prev_size_) {
            prev_size_ = 0;
            prev_off_ = 0;
        }

        if (prev_off_ > 0) {
            file.seek(prev_off_);
        }

        QByteArray arr = file.readAll();
        socket_.write(arr);

        prev_size_ = cursz;
        prev_off_ = cursz;

        needs_pub_ = false;
        file.close();
    }
}

void NetLogPumper::onFileChanged(const QString &path)
{
    needs_pub_ = true;   
}

void NetLogPumper::start()
{
    if (!connecting_)
    {
        connecting_ = true;
        connected_ = false;
        std::cout << "Connecting" << std::endl;
        socket_.connectToHost("192.168.1.6", 31483); 
    }
}

void NetLogPumper::onTcpConnected()
{
    connected_ = true;
    std::cout << "Connected" << std::endl;
}


void NetLogPumper::onTcpDisconnected()
{
    std::cout << "Disconnected" << std::endl;
    connected_ = false;
    connecting_ = false;
    socket_.close();
    QTimer::singleShot(10*1000, this, &NetLogPumper::start);
}
    
void NetLogPumper::onTcpError(QAbstractSocket::SocketError socketError)
{
    std::cout << "Tcp error" << std::endl;
    connecting_ = false;
    socket_.close();
    QTimer::singleShot(10*1000, this, &NetLogPumper::start);
}


