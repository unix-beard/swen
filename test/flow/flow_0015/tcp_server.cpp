#include <unistd.h>
#include <syslog.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <dlfcn.h>
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
#include "plugin_command.h"


using response_t = std::optional<std::string>;
using command_handler_t = std::function<response_t(const std::string&)>;
using builtin_command_t = std::map<std::string, command_handler_t>;


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


builtin_command_t command_handler = { 
    {"bye", bye},
    {"dummy", dummy},
    {"ping", ping},
    {"wiypid", wiypid}
};


///////////////////////////////////////////////////////////////////////////////////////////////////
// PLUGIN COMMAND HANDLER 
///////////////////////////////////////////////////////////////////////////////////////////////////
class PluginCommandHandler
{
public:
    PluginCommandHandler(const std::string& plugin_path = "./")
        : plugin_path_(plugin_path)
    {}

    ~PluginCommandHandler()
    {
        for (auto& it : plugin_dl)
        {
            syslog(LOG_INFO, "Unloading plugin command: [%s]", it.first.c_str());
            destroy_t* destroy_plugin = (destroy_t*) dlsym(it.second, "destroy");
            const char* dlsym_error = dlerror();
            if (dlsym_error)
            {
                syslog(LOG_ERR, "%s", dlsym_error);
                continue;
            }

            destroy_plugin(plugin_cache_[it.first]);
            dlclose(it.second);
        }
    }

    response_t
    handle(const std::string& command)
    {
        if (is_loaded(command))
        {
            syslog(LOG_INFO, "Plugin command (%s) already loaded. Using plugin cache.", command.c_str());
            return plugin_cache_[command]->handle(command);
        }

        std::string cmd_path = plugin_path_ + command + ".so";
        void* plugin = dlopen(cmd_path.c_str(), RTLD_LAZY);

        if (!plugin)
            throw std::runtime_error(dlerror());

        // reset errors
        dlerror();
        
        // load the symbols
        create_t* create_plugin = (create_t*) dlsym(plugin, "create");
        const char* dlsym_error = dlerror();
        if (dlsym_error)
            throw std::runtime_error(dlsym_error);
        
        PluginCommand* p = create_plugin();
        plugin_cache_[command] = p;
        plugin_dl[command] = plugin;
        return p->handle(command);
    }

private:
    bool
    is_loaded(const std::string& command)
    {
        return plugin_cache_.find(command) != plugin_cache_.end(); 
    }

    std::string plugin_path_;
    std::map<std::string, PluginCommand*> plugin_cache_;
    std::map<std::string, void*> plugin_dl;
};
///////////////////////////////////////////////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////////////////////////////////////////////
// TCP SERVER
///////////////////////////////////////////////////////////////////////////////////////////////////
class TcpServer
{
public:
    TcpServer(const builtin_command_t& builtins, unsigned short port = 41234)
        : builtins_(builtins), port_(port)
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

    void
    serve()
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

            response_t resp = {};
            
            resp = (is_builtin_command(msg)) ? handle_builtin_command(msg) : handle_plugin_command(msg);

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
    bool
    is_builtin_command(const std::string& cmd)
    {
        return builtins_.find(cmd) != builtins_.end();
    }

    response_t
    handle_builtin_command(const std::string& msg)
    {
        syslog(LOG_INFO, "Handling built-in command: [%s]", msg.c_str());
        return builtins_[msg](msg);
    }

    response_t
    handle_plugin_command(const std::string& msg)
    {
        try
        {
            syslog(LOG_INFO, "Handling plugin command: [%s]", msg.c_str());
            return plugin_handler_.handle(msg);
        }
        catch (std::exception& ex)
        {
            syslog(LOG_ERR, "%s", ex.what());
        }

        return {};
    }

    builtin_command_t builtins_;
    PluginCommandHandler plugin_handler_;

    int sock_;
    int newsock_;
    unsigned short port_;
    struct sockaddr_in srv_addr_;
    struct sockaddr_in cli_addr_;
};

///////////////////////////////////////////////////////////////////////////////////////////////////


void
daemonize()
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
    //chdir("/");

    int dev_null_fd;
    if ((dev_null_fd = open("/dev/null", O_RDWR)))
    {
        dup2 (dev_null_fd, STDIN_FILENO);
        dup2 (dev_null_fd, STDOUT_FILENO);
        dup2 (dev_null_fd, STDERR_FILENO);
        close(dev_null_fd);
    }
}


int
main(int argc, char *argv[])
{
    daemonize();

    setlogmask(LOG_UPTO (LOG_INFO));
    openlog("tcp_server", LOG_CONS | LOG_PID | LOG_NDELAY, LOG_LOCAL1);

    try
    {
        TcpServer tcp_server = TcpServer(command_handler);
        tcp_server.serve();
    }
    catch (std::exception& ex)
    {
        syslog(LOG_ERR, "Exception: %s", ex.what());
    }

    closelog();
}
