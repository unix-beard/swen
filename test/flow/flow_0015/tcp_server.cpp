#include <unistd.h>
#include <syslog.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <signal.h>
#include <cstdio>
#include <cstring>
#include <string>
#include <map>
#include <stdexcept>
#include <functional>
#include <iostream>
#include <optional>


using response_t = std::optional<std::string>;
using command_handler_t = std::function<response_t(const std::string&)>;


response_t
wiypid(const std::string& s)
{
    syslog(LOG_INFO, "Handling `wiypid` command");
    pid_t my_pid = getpid();
    syslog(LOG_INFO, "My PID: %d", my_pid);
    return std::make_optional(std::to_string(my_pid));
}

response_t
bye(const std::string& s)
{
    syslog(LOG_INFO, "Handling `bye` command");
    exit(0);
}

response_t
dummy(const std::string& s)
{
    syslog(LOG_INFO, "Handling `dummy` command");
    return {};
}

response_t
ping(const std::string& s)
{
    syslog(LOG_INFO, "Handling `ping` command. Responding with `pong`");
    return std::make_optional("pong");
}

std::map<std::string, command_handler_t> command_handler = { 
    {"bye", bye},
    {"dummy", dummy},
    {"ping", ping},
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

        syslog(LOG_INFO, "Server started (pid: %d, listening on port: %d)", getpid(), port_);
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
            syslog(LOG_INFO, "Message: %s", msg.c_str());

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

void daemonize()
{
    pid_t pid = fork();

    if (pid < 0)
        exit(EXIT_FAILURE);

    if (pid > 0)
        exit(EXIT_SUCCESS);

    if (setsid() < 0)
        exit(EXIT_FAILURE);

    // TODO: Setup signal handlers here

    pid = fork();

    if (pid < 0)
        exit(EXIT_FAILURE);

    if (pid > 0)
        exit(EXIT_SUCCESS);

    umask(0);
    chdir("/");

    int dev_null_fd;
    if (dev_null_fd = open("/dev/null", O_RDWR))
    {
        dup2 (dev_null_fd, STDIN_FILENO);
        dup2 (dev_null_fd, STDOUT_FILENO);
        dup2 (dev_null_fd, STDERR_FILENO);
        close(dev_null_fd);
    }
}

int main(int argc, char *argv[])
{
    daemonize();

    setlogmask(LOG_UPTO (LOG_INFO));
    openlog("tcp_server", LOG_CONS | LOG_PID | LOG_NDELAY, LOG_LOCAL1);
    try
    {
        TcpServer tcp_server;
        tcp_server.serve();
    }
    catch (std::exception& ex)
    {
        syslog(LOG_ERR, "Exception: %s", ex.what());
    }

    closelog();
}
