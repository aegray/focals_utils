#ifndef DOWNLOADER_H
#define DOWNLOADER_H

#include <QObject>
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QUrl>
#include <QDateTime>
#include <QFile>
#include <QDebug>


class Downloader : public QObject
{
    Q_OBJECT
public:
    explicit Downloader(const char *cert_path = nullptr, QObject *parent = 0);

    void doDownload();

signals:

public slots:
    void replyFinished (QNetworkReply *reply);
    void regSslError (QNetworkReply *reply, const QList<QSslError> &);

private:
    const char *certpath_;
    QNetworkAccessManager *manager;
};



#endif
