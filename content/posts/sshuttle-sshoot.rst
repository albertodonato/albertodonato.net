==============
Zero-setup VPN
==============

:date: 2015-06-15
:category: network
:tags: vpn, ssh, server

VPN_\s are a great tool to access resources on a remote network as if they were
local.

Working remotely, I use them a lot, and even to access my home network when I'm
away.

Even though open-source projects like OpenVPN_ have made it quite easy to set up
your own VPN server and configure clients to connect to it, they still require
some setup, and an additional opened port for the VPN service.

A pretty handy VPN tool I've been using quite a lot lately is sshuttle_.

``sshuttle`` is basically VPN-over-SSH. SSH is usually available out of the box
on any server machine (physical machines, cloud instances, containers), and can
be easily installed where it is not (like desktop machines) with a single
command.

``sshuttle`` requires no server-side setup or special privileges on the remote
host: if you can SSH into a machine, you can use ``sshuttle`` too.  It creates
an SSH tunnel and forwards traffic for specific networks from the local machine
to the remote server.


Creating a VPN connection
-------------------------

``sshuttle`` is pretty simple to use, for instance:

.. code:: console

  $ sshuttle 10.0.1.0/24 10.0.2.0/24 --remote=remote.example.com --auto-hosts

will forward traffic for the ``10.0.1.0/24`` and ``10.0.2.0/24`` subnets
through ``remote.example.com``, so that all machines on that network that are
accessible from the server machine, will be accessible from the remote host
too.

The ``--auto-hosts`` option is a pretty handy one: it automatically adds
discovered hostnames to the machine's ``/etc/hosts``, so that they can be used
in place of IP addresses.

Since ``sshuttle`` uses SSH under the hood, any user configuration from
``~/.ssh/config`` is respected.


Using a lot of ``sshuttle``\s?
------------------------------

After ending up with various shell scripts to start/stop ``sshuttle``
connections to different networks (with different configurations), I thought
I'd write a simple tool to manage all ``shuttle`` connections, and easily check
out which ones are connected: it's called sshoot_.

``sshoot`` is basically a connection manager for ``sshuttle``: it lets you
define profiles, using the same command line options that would be passed to
``sshuttle``:

.. code:: console

   $ sshoot create --remote=remote.example.com --auto-hosts vpn1 10.0.1.0/24 10.0.2.0/24

and start/stop the connection using the profile name:

.. code:: console

  $ sshoot start vpn1
  Profile started
  $ sshoot stop vpn1
  Profile stopped

It's also possible to check which profiles are defined and connected

.. code:: console

  $ sshoot list
     Profile  Remote host          Subnets
  ----------------------------------------------------------
   * vpn1     remote.example.com   10.0.1.0/24 10.0.2.0/24
     vpn2     remote2.example.com  192.168.9.0/24

In this case, the first profile is currently connected.


Installing ``sshoot``
---------------------

``sshoot`` can be easily installed from source:

.. code:: console

  $ git clone https://bitbucket.org/ack/sshoot.git
  $ cd sshoot
  $ python3 setup.py install

For latest Ubuntu releases, packages are also available from the PPA_.
To install from packages:

.. code:: console

  $ sudo apt-add-repository ppa:sshoot/stable
  $ sudo apt-get update
  $ sudo apt-get install sshoot

That's it!


.. _VPN: https://en.wikipedia.org/wiki/Virtual_private_network
.. _OpenVPN: https://openvpn.net/
.. _sshuttle: https://github.com/apenwarr/sshuttle
.. _sshoot: https://github.com/albertodonato/sshoot
.. _PPA: https://launchpad.net/~sshoot/+archive/ubuntu/stable
