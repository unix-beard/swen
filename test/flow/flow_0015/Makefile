CXX = g++-7
CXXFLAGS = -Wall -Werror -std=c++17
TARGETS = tcp_server dummy_plugin

all: $(TARGETS)

tcp_server: tcp_server.cpp plugin_command.h
	$(CXX) $(CXXFLAGS) -o tcp_server tcp_server.cpp -ldl

dummy_plugin: dummy_plugin.cpp plugin_command.h
	$(CXX) $(CXXFLAGS) -shared -fPIC -o dummy_plugin.so dummy_plugin.cpp

clean:
	rm -f tcp_server *.so

.PHONY: clean
