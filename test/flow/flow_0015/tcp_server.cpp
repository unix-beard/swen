#include <cstdio>
#include <cstring>
#include <string>
#include <unistd.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <stdexcept>
#include <map>
#include <functional>
#include <iostream>
#include <optional>


using response_t = std::optional<std::string>;
using command_handler_t = std::function<response_t(const std::string&)>;


response_t
wiypid(const std::string& s)
{
    std::cout << "Handling `wiypid` command\n";
    int my_pid = getpid();
    std::cout << "My process ID: " << my_pid << "\n";
    return std::make_optional(std::to_string(my_pid));
}

response_t
bye(const std::string& s)
{
    std::cout << "Handling `bye` command\n";
    exit(0);
}

response_t
dummy(const std::string& s)
{
    std::cout << "Handling `dummy` command\n";
    return {};
}

std::map<std::string, command_handler_t> command_handler = { 
    {"bye", bye},
    {"dummy", dummy},
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

            response_t resp = command_handler[msg](msg);
            if (resp)
            {
                std::string val = *resp;
                n = write(newsock_, val.c_str(), val.size());
            }

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
