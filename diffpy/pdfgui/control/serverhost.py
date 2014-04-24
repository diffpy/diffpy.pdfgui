#!/usr/bin/env python
##############################################################################
#
# PDFgui            by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2006 trustees of the Michigan State University.
#                   All rights reserved.
#
# File coded by:    Jiwu Liu
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

from diffpy.pdfgui.control.controlerrors import *
from diffpy.pdfgui.control.pdfcomponent import PDFComponent

class ServerHost(PDFComponent):
    """ServerHost holds the information about a remote machine where the
    pdfserver process is running. It can host multiple remote pdfserver.

    Data members:

    servers:    a list of local representatives of remote pdfserver instances
    config:     configuration dictionary of remote host
    connection: a ssh2 connection to remote host
    """
    class Server(object):
        """Server is the local represetative of a remote pdfserver

        pdfserver: a xmlrpclib.ServerProxy to pdfserver
        address: a host:port string
        busy: True if it is in use, otherwise False
        running: True if it is running
        connection: a ssh2 connection to remote host
        port: remote port where pdfserver is servicing
        """
        def __init__(self, connection):
            """Initialize the remote server

            connection -- a ssh2 connection to remote host
            """
            self.connection = connection
            self.pdfserver = None
            self.port = -1
            self.address = ''

            # One server can only service one fitting request at a time
            # by default, create and use
            self.busy = True
            self.running = False

            self.__start()

        def __start(self):
            """Start remote pdfserver. pdfserver.py must be in the user's PATH.
            It chooses the remote port on which it is running.
            """
            command = "pdffit2server"
            output = self.connection.execute(command)
            try:
                self.port = int(output.splitlines()[0])
            except (IndexError,ValueError):
                raise ControlRuntimeError, \
                "Unrecognized output from remote host %s: "%self.connection.host + output
            return

        def connect(self):
            """Set up XMLRPC ServerProxy and test connection.
            """
            from xmlrpclib import ServerProxy
            self.address = "http://%s:%i"%(self.connection.host, self.port)
            transport = self.connection.getXMLRPCTransport()
            self.pdfserver = ServerProxy(self.address,transport)

            import time

            # now keep polling if the server is up ( test for 15 seconds)
            counter = 5
            while counter > 0 and not self.running:
                if self.connection.owner.quit:
                    return
                try:
                    # server started slowly, allow 3 seconds in the beginning
                    time.sleep(3)
                    self.running = self.pdfserver.isRunning()
                    counter = -1
                except ControlConnectError:
                    counter -= 1


            if counter == 0:
                raise ControlRuntimeError, \
                    "Can not connect to pdferver@'%s'"%self.connection.host

        def close(self):
            """Kill the server"""
            if self.running:
                self.pdfserver.kill_server()
            return
    # End of class Server

    def __init__(self, name, config):
        """initialize

        name -- component name
        config -- configuration for this proxy
        """
        if name is None:
            name = 'ServerHost'

        PDFComponent.__init__(self, name)
        self.config = config

        import threading
        self.lock = threading.RLock()
        self.servers = []

        from diffpy.pdfgui.control.connection import Connection
        self.connection = Connection(self)

        self.quit = False
        return

    def getServer(self, bWait=False):
        """Get a pdfserver proxy

        bWait -- wait for server or not (default False)
        return: a pdfserver proxy
        """
        try:
            self.lock.acquire()
            for server in self.servers:
                if not server.busy and server.running:
                    server.busy = True
                    return server.pdfserver
            else:
                # if self.servers is not empty and we'd like to wait
                if bWait and self.servers:
                    #FIXME: a semaphore should be created so that we can wait here
                    pass
                else:
                    # i need a new one
                    server = ServerHost.Server(self.getConnection())
                    server.connect() # connect to pdfserver
                    self.servers.append(server)
                    return server.pdfserver
        finally:
            self.lock.release()

        return None

    def releaseServer(self, pdfserver):
        """Release a pdfserver proxy

        pdfserver -- a pdfserver proxy
        """
        try:
            self.lock.acquire()
            for server in self.servers:
                if server.pdfserver is pdfserver:
                    server.busy = False
                    break
        finally:
            self.lock.release()
        return

    def close(self, force = False):
        """shut down connection to remote host

        force -- if shut down forcefully
        """
        self.quit = True
        try:
            self.lock.acquire()
            #make a copy to traverse
            for server in self.servers[:]:
                if server.busy and not force:
                    # we can not close it because some fittings are still use its tunnel
                    raise ControlStatusError, "ServerHost: %s is busy"%self.name
                else:
                    server.close()
                    self.servers.remove(server)
        finally:
            self.lock.release()

        self.connection.close()
        return

    def onError(self, address):
        """handle the error from connection

        address -- remote pdfserver address
        """
        try:
            self.lock.acquire()
            for server in self.servers:
                if server.address == address:
                    server.running = False
        finally:
            self.lock.release()

    def getConnection(self):
        """Get a verified and connected ssh transport.

        This tries to establish an ssh connection using the ssh2 protocol with a
        preconfigured host. This uses paramiko's Agent class, which may work
        differently on Windows.

        return value: connection
        """
        if self.connection.isConnected():
            return self.connection

        # otherwise, reconnect to remote host
        import os
        from diffpy.pdfgui.control.connection import Connection
        try:
            # extract info from configuration
            host = self.config['host']
            user = self.config['username']
            auth = self.config['authentication']
            if self.config['use_default_port']:
                port = Connection.DefaultPort
            else:
                port = int(self.config['port'])

            if auth == Connection.PSWDAUTH:
                passwd = self.config['password']
                self.connection.connect(host,user,port,auth,passwd=passwd)
            else: # RSA or DSA
                if self.config['use_default_path']:
                    keyFile = os.environ['HOME'] + '/.ssh/id_rsa'
                else:
                    keyFile = self.config['path']
                passphrase = self.config.get('passphrase', None)
                self.connection.connect(host,user,port,auth,keyFile=keyFile,
                                        passphrase = passphrase)
        except KeyError, error:
            raise ControlConfigError,\
            "ServerHost: '%s' doesn't have key '%s'"%(self.name, str(error))

        return self.connection


if __name__ == '__main__':
    import sys
    import getopt
    import getpass
    from diffpy.pdfgui.control.connection import Connection
    def _usage():
        print "Usage: %s [-u user@host] [-p(passwd)|-r(rsa)|-d(dsa)]"%sys.argv[0]

    # parse arguments
    try:
        optlist, args = getopt.getopt(sys.argv[1:], "u:prd" )
    except getopt.GetOptError:
        usage()
        sys.exit(1)

    user = getpass.getuser()
    host = 'localhost'
    auth = Connection.RSAAUTH
    for o,a in optlist:
        if o == '-u':
            user,host = a.split('@')
        elif o == '-p':
            auth = Connection.PSWDAUTH
        elif o == '-r':
            auth = Connection.RSAAUTH
        elif o == '-d':
            auth = Connection.DSAAUTH

    config = {
                'use_default_port'  :   True,
                'use_default_path'  :   True,
                'host'              :   host,
                'authentication'    :   auth,
                'username'          :   user,
             }
    if auth == Connection.PSWDAUTH:
        config ['password'] = getpass.getpass("Password: ")

    proxy = ServerHost(host,config)
    pdfserver = proxy.getServer()
    #print "pdfserver.isRunning():", pdfserver.isRunning()
    print "pdfserver.reset():", pdfserver.reset()
    proxy.close(True)
    print 'Session closed.'

# End of file
