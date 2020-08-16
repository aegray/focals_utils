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



    //connect(&socket_, &QAbstractSocket::disconnected, this, &NetController::onTcpDisconnected);
    //connect(&socket_, &QAbstractSocket::error, this, &NetController::onTcpError);
    //connect(&socket_, &QIODevice::readyRead, this, &NetController::onTcpReadyRead);

    //connect(&socket_, &QIODevice::bytesWritten,
    //        this, &NetController::onTcpBytesWritten);
}

void NetController::reset_state()
{
    state_ = 0;  
    expect_next_bytes_ = 0;
    current_build.clear();
    buffer.clear();
}

void NetController::start()
{
    if (!connecting_)
    {
        connecting_ = true;
        std::cout << "Connecting" << std::endl;
        socket_.connectToHost("192.168.1.6", 31482); 
    }
}

void NetController::onTcpConnected()
{
    reset_state();
    std::cout << "Connected" << std::endl;
}

void NetController::onTcpReadyRead()
{
    auto data = socket_.readAll();
    buffer.append(data);
  
    int rem = buffer.length();

    //std::cout << "Got: " << data.length() << " bytes.  To process=" << rem << ". state=" << state_ << std::endl;
    int onind = 0;

    const char *dataptr = buffer.constData();
    while (rem > 0)
    {
        if (state_ == 0) // waiting cmd
        {
            if (data[onind] == 'c')
            {
                std::cout << "Got command: moving to state 1" << std::endl;
                // receive cmd
                state_ = 1;
                rem -= 1;
                onind += 1;
                
                if (rem == 0)
                {
                    buffer.clear();
                }
            }
            else if (data[onind] == 's')
            {
                std::cout << "Got send: moving to state 3" << std::endl;
                // receive cmd
                state_ = 3;
                rem -= 1;
                onind += 1;
                
                if (rem == 0)
                {
                    buffer.clear();
                }
            }
        }
        else if (state_ == 1) // got comand start wait length
        {
            if (rem >= 4)
            {
                std::cout << "Reading cmd len: " << std::endl;

                char buf[4];
                for (int i = 0; i < 4; ++i)
                {
                    buf[i] = dataptr[onind+i];
                }
                unsigned cmdlen = *reinterpret_cast<const unsigned *>(buf); //&bdataptr[onind]);

                expect_next_bytes_ = cmdlen;
                rem -= 4;
                onind += 4;
                state_ = 2;

                current_build.clear();
                if (rem == 0)
                {
                    buffer.clear();
                }

            }
            else
            {
                std::cout << "Out of data, will read rest of command on the next go" << std::endl;
                buffer = buffer.right(rem);
                rem = 0;
            }
        }
        else if (state_ == 2)
        {
            if (rem >= expect_next_bytes_)
            {
                std::cout << "Reading remainder of cmd: " << expect_next_bytes_ << std::endl;
                for (int i = 0; i < expect_next_bytes_; ++i)
                {
                    current_build.append(dataptr[onind+i]);
                }
                current_build.append(' ');
                current_build.append('&');
                current_build.append(' ');
                current_build.append('\0');
                std::cout << "Got cmd: " << current_build.constData() << std::endl;
                system(current_build.constData());
                std::cout << " continuing..." << std::endl;


                socket_.write("X", 1);
                socket_.write("Y", 1);
                                                
                socket_.flush();


                current_build.clear();
                onind += expect_next_bytes_;
                rem -= expect_next_bytes_;
                expect_next_bytes_ = 0;

                if (rem == 0)
                {
                    buffer.clear();
                }

                state_ = 0;
            }
            else
            {
                std::cout << "Out of data, appending to buffer and processing next time" << std::endl;
                current_build.append(buffer.right(rem));

                buffer.clear();

                expect_next_bytes_ -= rem;
                rem = 0;
            }
        }
        else if (state_ == 3)
        {
            if (rem >= 4)
            {
                std::cout << "Reading fname len: " << std::endl;

                char buf[4];
                for (int i = 0; i < 4; ++i)
                {
                    buf[i] = dataptr[onind+i];
                }
                unsigned fnamelen = *reinterpret_cast<const unsigned *>(buf); //&bdataptr[onind]);

                expect_next_bytes_ = fnamelen;
                rem -= 4;
                onind += 4;
                state_ = 4;

                current_build.clear();
                if (rem == 0)
                {
                    buffer.clear();
                }

            }
            else
            {
                std::cout << "Out of data, will read rest of fname on the next go" << std::endl;
                buffer = buffer.right(rem);
                rem = 0;
            }
        }
        else if (state_ == 4)
        {
            if (rem >= expect_next_bytes_)
            {
                std::cout << "Reading remainder of fname: " << expect_next_bytes_ << std::endl;
                for (int i = 0; i < expect_next_bytes_; ++i)
                {
                    current_build.append(dataptr[onind+i]);
                }
                current_build.append('\0');
                std::cout << "Got fname: " << current_build.constData() << std::endl;

                filename_ = current_build.constData();
                
                outfile_ = new std::ofstream(filename_, std::ios::out | std::ios::binary);


                current_build.clear();
                onind += expect_next_bytes_;
                rem -= expect_next_bytes_;
                expect_next_bytes_ = 0;

                if (rem == 0)
                {
                    buffer.clear();
                }

                state_ = 5;
            }
            else
            {
                std::cout << "Out of data, appending to buffer and processing next time" << std::endl;
                current_build.append(buffer.right(rem));

                buffer.clear();

                expect_next_bytes_ -= rem;
                rem = 0;
            }
        }
        else if (state_ == 5)
        {
            if (rem >= 4)
            {

                char buf[4];
                for (int i = 0; i < 4; ++i)
                {
                    buf[i] = dataptr[onind+i];
                }
                unsigned datalen = *reinterpret_cast<const unsigned *>(buf); //&bdataptr[onind]);
                std::cout << "Reading data: total=" << datalen << std::endl;

                expect_data_bytes_ = datalen;
                rem -= 4;
                onind += 4;
                state_ = 6;


                if (rem == 0)
                {
                    buffer.clear();
                }

            }
            else
            {
                std::cout << "Out of data, will read rest of fname on the next go" << std::endl;
                buffer = buffer.right(rem);
                rem = 0;
            }
        }
        else if (state_ == 6)
        {
            unsigned to_read = std::min(expect_data_bytes_, (unsigned)rem);
            outfile_->write(&dataptr[onind], to_read);
            expect_data_bytes_ -= to_read;
            rem -= to_read;
            onind += to_read;

            if (expect_data_bytes_ == 0)
            {
                std::cout << "Finished writing" << std::endl;
                outfile_->flush();
                outfile_->close();
                delete outfile_;
                expect_data_bytes_ = 0;

                socket_.write("M", 1);
                socket_.write("F", 1);
                socket_.flush();

                state_ = 0;
            }


            if (rem == 0)
            {
                buffer.clear();
            }
        }
    }

//
//    char buffer[10*1024];
//    qint64 len = 0;
//    while ((len = socket_.readLine(buffer, sizeof(buffer)))  > 0)
//    {
//        std::cout << "Received: " << buffer << std::endl;
//    }
}

void NetController::onTcpDisconnected()
{
    std::cout << "Disconnected" << std::endl;
    connecting_ = false;
    socket_.close();
    QTimer::singleShot(10*1000, this, &NetController::start);
}
    
void NetController::onTcpError(QAbstractSocket::SocketError socketError)
{
    std::cout << "Tcp error" << std::endl;
    connecting_ = false;
    socket_.close();
    QTimer::singleShot(10*1000, this, &NetController::start);
}


