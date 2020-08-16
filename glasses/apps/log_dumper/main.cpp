
#include <iostream>
#include <QCoreApplication>

#include <QtNetwork/QNetworkAccessManager>
#include <QUrl>
#include <QtNetwork/QNetworkRequest>
#include <QtNetwork/QNetworkReply>
#include <QEventLoop>

#include "NetLogPumper.h"


int main(int argc, char * argv[])
{
    QCoreApplication app(argc, argv);

    NetLogPumper d;
    d.start();
    
    return app.exec();
}
