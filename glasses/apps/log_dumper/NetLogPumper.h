#ifndef DOWNLOADER_H
#define DOWNLOADER_H

#include <QObject>
#include <QUrl>
#include <QDateTime>
#include <QFile>
#include <QDebug>
#include <QTimer>

#include <QTcpSocket>
#include <QFileSystemWatcher>


class NetLogPumper : public QObject
{
    Q_OBJECT
public:
    explicit NetLogPumper(QObject *parent = 0);

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

    //void onTcpReadyRead();
//    void onTcpBytesWritten(qint64 numBytes);
    void onTcpError(QAbstractSocket::SocketError socketError);

    void onFileChanged(const QString &path);
    void onTimer();


//signals:

//public slots:
//    void replyFinished (QNetworkReply *reply);
//    void regSslError (QNetworkReply *reply, const QList<QSslError> &);

private:
    int prev_size_ = 0;
    int prev_off_ = 0;
    bool needs_pub_ = false;


    QFileSystemWatcher file_watcher_;
    QTcpSocket socket_;
    QTimer timer_;


    bool connecting_ = false;
    bool connected_ = false;

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
