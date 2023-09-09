#include <QGuiApplication>
#include <QTimer>
#include <iostream>


void printer()
{
    std::cout << "HELLO" << std::endl;
    QCoreApplication::quit();
}

int main(int argc, char **argv)
{
    QCoreApplication app(argc, argv); 
    QTimer::singleShot(2000, printer);
    return app.exec();
}
