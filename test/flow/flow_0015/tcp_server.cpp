#include <cstdio>
#include <cstring>
#include <unistd.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <stdexcept>
#include <map>
#include <functional>
#include <iostream>


void wiypid(const std::string& s)
{
    std::cout << "Handling wiypid command\n";
    std::cout << "My process ID: " << getpid() << "\n";
}

void bye(const std::string& s)
{
    std::cout << "Handling bye command\n";
    exit(0);
}

std::map<std::string, std::function<void(const std::string&)>> command_handler = { 
    {"bye", bye},
    {"wiypid", wiypid}
};


class TcpServer
{
public:
    explicit TcpServer(unsigned short port = 41234)
        : port_(port)
    {
        sock_ = socket(AF_INET, SOCK_STREAM, 0);

        if (sock_ < 0)
            throw std::runtime_error("Can't open socket");

        srv_addr_.sin_family = AF_INET;
        srv_addr_.sin_addr.s_addr = INADDR_ANY;
        srv_addr_.sin_port = htons(port_);

        if (bind(sock_, (struct sockaddr*) &srv_addr_, sizeof(srv_addr_)) < 0) 
            throw std::runtime_error("Can't bind");
    }

    ~TcpServer()
    {
        close(newsock_);
        close(sock_);
    }

    void serve()
    {
        for (;;)
        {
            listen(sock_, 5);
            socklen_t clilen = sizeof(cli_addr_);
            newsock_ = accept(sock_, (struct sockaddr *) &cli_addr_, &clilen);

            if (newsock_ < 0) 
                throw std::runtime_error("Can't accept connection");

            char buffer[256];
            bzero(buffer, 256);
            int n = read(newsock_, buffer, 255);

            if (n < 0)
                throw std::runtime_error("Can't read from socket");

            std::string msg(buffer);
            std::cout << "Here is the message: " << msg << "\n";
            n = write(newsock_,"I got your message", 18);
            command_handler[msg](msg);

            if (n < 0)
                throw std::runtime_error("Can't write to socket");
         }
    }

private:
    int sock_;
    int newsock_;
    unsigned short port_;
    struct sockaddr_in srv_addr_;
    struct sockaddr_in cli_addr_;
};


int main(int argc, char *argv[])
{
    TcpServer tcp_server;
    tcp_server.serve();
}
