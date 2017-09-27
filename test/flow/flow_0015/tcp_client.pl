#!/usr/bin/env perl

use IO::Socket::INET;
use Getopt::Long;


# Command to send to a server
my $command = 'ping';

GetOptions("command|c=s" => \$command)
    or die("Error in command line arguments");
 
# auto-flush on socket
$| = 1;
 
# create a connecting socket
my $socket = new IO::Socket::INET (
    PeerHost => 'localhost',
    PeerPort => '41234',
    Proto => 'tcp',
);

die "cannot connect to the server: $!\n" unless $socket;

print "connected to the server\n";
              
my $size = $socket->send($command);
print "sent command [$command] of length $size\n";
 
# notify server that request has been sent
shutdown($socket, 1);
  
# receive a response of up to 1024 characters from server
my $response = "";
$socket->recv($response, 1024);
print "received response: $response\n";
 
$socket->close();
