#include "downloader.h"

#include <QCoreApplication>

//#define NOSSL

Downloader::Downloader(const char *certpath, QObject *parent) :
    QObject(parent), certpath_(certpath)
{
}

void Downloader::doDownload()
{
    manager = new QNetworkAccessManager(this);
    connect(manager, SIGNAL(finished(QNetworkReply*)),
            this, SLOT(replyFinished(QNetworkReply*)));

    if (certpath_)
    {
        QSslConfiguration sslconfig;                                                                        
        sslconfig.setCaCertificates(QSslCertificate::fromPath(certpath_));
        //sslconfig.setPeerVerifyMode(QSslSocket::VerifyNone);

        connect(manager, SIGNAL(sslErrors(QNetworkReply*, const QList<QSslError> &)), 
                this, SLOT(regSslError(QNetworkReply*, const QList<QSslError> &)));
        QNetworkRequest req(QUrl("https://bysouth.com:4443/index.html"));
        req.setSslConfiguration(sslconfig);
        manager->get(req); 
    }
    else
    {
        QNetworkRequest req(QUrl("http://bysouth.com:4443/index.html"));
        manager->get(req); 
    }
}
    
void Downloader::regSslError (QNetworkReply*, const QList<QSslError> &errl)
{
    for (auto x : errl)
    {
        qDebug() << x;
    }
}

void Downloader::replyFinished (QNetworkReply *reply)
{
    if(reply->error())
    {
        qDebug() << "ERROR!";
        qDebug() << reply->errorString();
    }
    else
    {
        qDebug() << reply->header(QNetworkRequest::ContentTypeHeader).toString();
        qDebug() << reply->header(QNetworkRequest::LastModifiedHeader).toDateTime().toString();
        qDebug() << reply->header(QNetworkRequest::ContentLengthHeader).toULongLong();
        qDebug() << reply->attribute(QNetworkRequest::HttpStatusCodeAttribute).toInt();
        qDebug() << reply->attribute(QNetworkRequest::HttpReasonPhraseAttribute).toString();

        qDebug() << reply->readAll();
    }

    reply->deleteLater();
    QCoreApplication::quit();
}


