
#include <iostream>
#include <QCoreApplication>

#include "downloader.h"


int main(int argc, char * argv[])
{
    QCoreApplication app(argc, argv);

    Downloader d((argc > 1) ? argv[1] : ((const char*)nullptr));
    d.doDownload();
    
    return app.exec();
}
