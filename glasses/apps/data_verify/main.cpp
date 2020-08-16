
#include <iostream>
#include <QCoreApplication>

#include <QtNetwork/QNetworkAccessManager>
#include <QUrl>
#include <QtNetwork/QNetworkRequest>
#include <QtNetwork/QNetworkReply>
#include <QEventLoop>

#include "NetController.h"
//#include <QNetworkReply>
//#include <QEventLoop>
//#include <QString>
//


//socket = new QSslSocket(this);
//QFile certfile("D:\\hani\\cert\\localhost.localdomain.pem");
//Q_ASSERT(certfile.open(QIODevice::ReadOnly));
//QList<QSslCertificate> certList;
//QSslCertificate cert(&certfile,QSsl::Pem);
//certList.append(cert);
//socket->addCaCertificate(cert);
//socket->setCaCertificates(certList);
//QList<QSslCertificate> serverCert = socket->caCertificates();
//


int main(int argc, char * argv[])
{
    QCoreApplication app(argc, argv);

    NetController d;
    //d.start();
    
    return app.exec();
//
//    QNetworkAccessManager manager;
//    QNetworkReply *response = manager.get(QNetworkRequest(QUrl("http://google.com")));
//    QEventLoop event;
//    QObject::connect(response,SIGNAL(finished()),&event,SLOT(quit()));
//    event.exec();
//    QString html = response->readAll();
//
//    std::string data = html.toUtf8().constData();
//    std::cout << data << std::endl;
}
