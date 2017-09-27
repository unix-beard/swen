#include "plugin_command.h"

class DummyPlugin : public PluginCommand
{
public:
    response_t
    handle(const std::string& msg) override
    {
        return std::make_optional("Hello from dummy plugin!");
    }
};


extern "C" PluginCommand* create() {
    return new DummyPlugin;
}

extern "C" void destroy(PluginCommand* p) {
    delete p;
}

