#ifndef DOWNLOADER_H
#define DOWNLOADER_H

#include <QObject>
//#include <QNetworkAccessManager>
//#include <QNetworkRequest>
//#include <QNetworkReply>
#include <QUrl>
#include <QDateTime>
#include <QFile>
#include <QDebug>

#include <QTcpSocket>


class NetController : public QObject
{
    Q_OBJECT
public:
    explicit NetController(QObject *parent = 0);

	//void start();

    void reset_state();

    
public slots:
    void start();
    //void acceptConnection();
    //void startTransfer();
    //void updateServerProgress();
    //void updateClientProgress(qint64 numBytes);
    //void displayError(QAbstractSocket::SocketError socketError);

    void onTcpConnected();
    void onTcpDisconnected();

    void onTcpReadyRead();
//    void onTcpBytesWritten(qint64 numBytes);
    void onTcpError(QAbstractSocket::SocketError socketError);



//signals:

//public slots:
//    void replyFinished (QNetworkReply *reply);
//    void regSslError (QNetworkReply *reply, const QList<QSslError> &);

private:
    QTcpSocket socket_;
    bool connecting_ = false;

    int state_ = 0;
    // 0 = waiting cmd
    // 1 = got command start, wait length
    // 2 = got command len, waiting cmd data
    
    // 3 = got send start, waiting fname len
    // 4 = got fname len, waiting fname
    // 5 = got fname, waiting data len
    // 6 = got data len, waiting data
    //
    //
    //
    // in processing command
    unsigned expect_next_bytes_ = 0;
    unsigned expect_data_bytes_ = 0;

    QByteArray buffer;
    QByteArray current_build;

    std::string filename_;
    std::ofstream *outfile_;
};



#endif
