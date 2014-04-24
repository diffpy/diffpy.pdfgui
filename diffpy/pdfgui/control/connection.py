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

import xmlrpclib
import httplib
import socket

from diffpy.pdfgui.control.controlerrors import *

RemoteExecution = 0
try:
    import paramiko
    RemoteExecution = 1
    #paramiko.util.log_to_file("/tmp/paramiko.log")
except ImportError:
    # no remote execution available
    pass

class _RawTunnel(object):
    """A class simulates xmlrpclib.Transport. It wrapps up a paramiko channel to
    provide a Transport interface.
    """
    def __init__(self, conn):
        """initialize

        conn -- Connection object
        """
        self.conn = conn

    def request(self, address, handler, request_body, verbose=0):
        """function to handle XMLRPC request

        address -- string of hostname:port for remote host
        handler --
        request_body -- xml encoded request
        verbose -- if it is 1, print verbose information
        """
        chan = self.conn.openTunnel(address)
        # use a file interface to read/write
        f = chan.makefile('rw')
        header = "POST /%s HTTP/1.1\n"%handler
        header += "User-Agent: PDFGUI\n"
        header += "Host: %s\n"%address
        header += "Content-Type: text/xml\n"
        header += "Content-Length: %d\n\n"%len(request_body)

        try:
            f.write(header)
            f.write(request_body)
            f.flush()
            return self._parse(f, chan)
        except (xmlrpclib.Error, socket.error, Exception),err:
            self.conn.owner.onError(address)
            raise ControlConnectError, "XMLRPC Connection error: " + str(err)

    def _parse(self, f, chan):
        n = 0
        line = f.readline()
        if line.split()[1] != '200':
            raise ControlConnectError, 'HTTP request failed' + line

        while n == 0:
            if line.lower().startswith('content-length:'):
                n = int(line[15:].strip())
            line = f.readline()
        content = f.read(n)
        f.close()
        chan.close()

        p, u = xmlrpclib.getparser()
        p.feed(content)
        p.close()
        return u.close()


class _WrapTunnel(xmlrpclib.Transport):
    """A overload class of xmlrpclib.Transport. It changes make_connection()
    method to use a paramiko channel instead of real socket
    """
    def __init__(self, conn):
        """initialize

        conn -- Connection object
        """
        self.conn = conn
        self.chan = None

    def make_connection(self, address):
        """make a HTTPConnection to remote host.

        address -- hostname:port
        """
        if self.chan is not None:
            # clean up the previous channel
            self.chan.close()
        self.chan = self.conn.openTunnel(address)
        h = httplib.HTTP(address)

        #IMPORTANT: set its socket to our chan to prevent real connection
        h._conn.sock = self.chan
        return h


class Connection:
    """SSH2 Connection and tunnel support

    Data member:
    transport: a paramiko transport object
    session: a paramiko session
    channel: a fake channel for HTTP transport through ssh tunnelling

    host: remote host name
    user: remote account user name
    port: remote port
    auth: authentication type
    passwd: password for remote account
    keyFile: local file for RSA/DSA keys
    passphrase: passphrase of RSA/DSA
    """
    DefaultPort = 22
    PSWDAUTH = 0
    RSAAUTH = 1
    DSAAUTH = 2

    def __init__(self, owner):
        """initialize

        owner -- object who starts the connection
        """
        self.owner = owner

        # channels
        self.transport = None
        self.session = None
        self.channel = None

        # settings
        self.host = None
        self.user = None
        self.port = Connection.DefaultPort
        self.auth = Connection.PSWDAUTH
        self.passwd = None
        self.keyFile = None
        self.passphrase = None

    def isConnected(self):
        """check if this connection is still alive
        """
        return self.transport is not None and self.transport.is_active()

    def connect(self, host, user, port, auth, passwd=None, keyFile=None, passphrase=None):
        """make a ssh2 connection to the remote host.

        host -- remote host machine
        user -- username
        port -- port of remote ssh service
        auth -- authenticate method, PSWDAUTH,RSAAUTH,DSAAUTH
        passwd --  only required if use PSWDAUTH
        keyFile -- only required if use RSAAUTH or DSAAUTH
        passphrase -- only required if use RSAAUTH or DSAAUTH, and passphrase is set
        """
        self.host = host
        self.user = user
        self.port = port
        self.auth = auth
        self.passwd = passwd
        self.keyFile = keyFile
        self.passphrase = passphrase

        try:
            transport = paramiko.Transport((self.host, self.port))
            transport.start_client()
            if auth == Connection.RSAAUTH:
                self.__rsa_auth(transport)
            elif auth == Connection.DSAAUTH:
                self.__dsa_auth(transport)
            else:
                # use password
                transport.auth_password(self.user, self.passwd)
                if not transport.is_authenticated():
                    raise ControlAuthError,\
                "Connection: '%s@%s' does not exist or password is wrong"%(self.user, self.host)
        except IOError:
            raise ControlFileError,\
            "Connection: can't open rsa/dsa file %s"%self.keyFile
        except (paramiko.SSHException, paramiko.BadAuthenticationType):
            raise ControlAuthError,\
            "Connection: '%s@%s' failed in authentication"%(self.user, self.host)
        except socket.error,errmsg:
            raise ControlConnectError,\
            "Connection: %s %s"%(self.host, errmsg)

        # setup the transport channel
        self.transport = transport
        # stay alive over NAT
        self.transport.set_keepalive(60)
        return

    def close(self):
        """close remote connection
        All the tunnel will be closed as well.
        """
        if self.transport:
            self.transport.close()

    def __rsa_auth(self,transport):
        """Authorize connection with default rsa key location.

        transport -- paramiko transport
        """
        try:
            key = paramiko.RSAKey.from_private_key_file(self.keyFile)
        except paramiko.PasswordRequiredException:
            if self.passphrase is not None:
                key = paramiko.RSAKey.from_private_key_file(self.keyFile, self.passphrase)
            else:
                raise ControlAuthError,\
            "Connection: '%s@%s' requires passphrase for RSA"%(self.user, self.host)
        transport.auth_publickey(self.user, key)
        return

    def __dsa_auth(self, transport):
        """Authorize connection with default dsa key location.

        transport -- paramiko transport
        """
        try:
            key = paramiko.DSAKey.from_private_key_file(self.keyFile)
        except paramiko.PasswordRequiredException:
            if self.passphrase is not None:
                key = paramiko.RSAKey.from_private_key_file(self.keyFile, self.passphrase)
            else:
                raise ControlAuthError,\
            "Connection: '%s@%s' requires passphrase for DSA"%(self.user, self.host)
        transport.auth_publickey(self.user, key)
        return

    def getXMLRPCTransport(self):
        """make a HTTP transport to remote host through SSH tunnelling.

        return: a xmlrpc  transport instance
        """
        if self.transport is None:
            raise ControlRuntimeError, "ssh connection not available"

        # else, use _WrapTunnel for this purpose
        return _RawTunnel(self)
        #return _WrapTunnel(self)

    def openTunnel(self, address):
        """As requested by xmlrpclib.Transport, open a ssh2 tunnel

        address -- host:port string
        return: a sshe tunnel
        """
        host,port = address.split(':')
        port = int (port)
        try:
            chan = self.transport.open_channel('direct-tcpip',(host,port), ('localhost',port))
        except paramiko.SSHException:
            chan = None
        if chan is None: # It is for backward compatibility of paramiko,
            raise ControlConnectError, "Can not open tunnel to '%s'"%address

        return chan

    def execute(self, cmd, n = 1024):
        """execute a command

        cmd -- command to be run remotely
        n -- size of output to be returned
        return -- output
        """
        self.session = self.transport.open_session()
        self.session.exec_command(cmd)

        # Check to see if the server started nicely
        exit_status = self.session.recv_exit_status()
        if exit_status:
            errmsg = self.session.recv_stderr(n)
            raise ControlRuntimeError, "Connection: '%s' failed: %s"% (cmd,errmsg)

        # Take the standard output from the server and get the port number.
        return self.session.recv(n)

# End of file
