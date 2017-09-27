#ifndef PLUGIN_COMMAND_H
#define PLUGIN_COMMAND_H

#include <string>
#include <functional>


using response_t = std::optional<std::string>;


class PluginCommand
{
public:
    virtual ~PluginCommand() {}
    virtual response_t handle(const std::string& msg) = 0;
};

// the types of the class factories
typedef PluginCommand* create_t();
typedef void destroy_t(PluginCommand*);

#endif
