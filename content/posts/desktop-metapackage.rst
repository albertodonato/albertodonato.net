=====================================
Install all needed packages in one go
=====================================

:date: 2016-04-09
:category: howto
:tags: deb, desktop, packaging, ubuntu

Installing a new workstation (or reinstalling one) is quite a boring task; the
OS setup itself is pretty quick, but then you have to install all the tools
and applications you use every day.

I end up reinstalling both my laptop and desktop quite often, almost every time
a new Ubuntu release comes out (both to check out the news in the installer and
to start with a fresh system); so at some point I started putting the list of
the packages I needed in a script, which would ``apt install`` them.  This was
a quick and simple solution that would allow me to install everything with a
single command.

But wouldn't it be nice to also have an automatic way to keep this list in sync
across multiple machines and be able to also remove packages if they become
unneeded?

To do that, `metapackages` are the perfect tool. They're just empty packages
that depend on other packages. Our list of packages just becomes a ``Depends``
directive in the metapackage.


Metapackages to the rescue
--------------------------

Building a metapackage is very easy, all you need is a tool named ``equivs``
and a few steps:

#. Install it

   .. code:: console

     $ sudo apt install equivs

#. Create a template control file for the package

   .. code:: console

     $ equivs-control ack-desktop.control

#. Edit the control file. Only a few lines are required, but at least at least
   ``Package``, ``Version``, ``Maintainer``, and ``Description`` should be
   filled.

   But the most important directive, as said, is ``Depends``. Here we must list
   all the packages we want to install.  The result is something like this:

   .. code:: text

     Package: ack-desktop
     Version: 1.0
     Maintainer: Alberto Donato <alberto.donato@gmail.com>
     Architecture: all
     Section: misc
     Priority: optional
     Depends:
      emacs-snapshot, emacs-snapshot-el,
      bpython, ipython, ipython3, python-pip, python-virtualenv,
      ...
     Description: metapackage for installation of my package selection.
      This installs a whole set of packages that I currently use on Ubuntu desktops.

#. Build the ``.deb`` package

   .. code:: console

     $ equivs-build ack-desktop.control

   which creates ``ack-desktop_1.0_all.deb`` in the current directory.

#. Install package and dependencies

   .. code:: console

     $ sudo dpkg -i ack-desktop_1.0_all.deb
     $ sudo apt install -f  # pull in all dependencies

#. Profit!


Whenever the list of needed packages changes, it's enough to update the control
file, rebuild and install the new package.

*IMPORTANT:* you need to increment the package version at every change.

A nice thing of this approach is that all dependencies will be marked as
automatically installed. So, if packages are removed from the list, ``apt``
will show them as "automatically installed and no longer needed", and ``sudo
apt autoremove`` will uninstall them.


Setting up a repository
-----------------------

Now, what about making these package available on multiple computers?

The easiest way is to create a Debian repository hosting the metapackages, and
make it available to all computers.  This way, just adding an `APT` source on
each machine will packages available everywhere, and they'll be updatable as
any other package in the distribution.

Setting up a repository for just a couple of packages might seem overkill, but
it's actually so simple that it's worth the effort.

A repository can be build and maintained with just few steps, using
``reprepro``.

#. Install it

   .. code:: console

     $ sudo apt install reprepro

#. Create the base directory of your repository (let's call it ``ubuntu/``),
   and a ``conf/`` directory in it. Then create a ``distributions`` file in
   this directory, which will contain the configuration for reprepro:

   .. code:: console

     $ tree ubuntu/
     ubuntu/
     └── conf
         └── distributions

     1 directory, 1 file

#. Edit the ``distributions`` file like this:

   .. code:: text

     Codename: unstable
     Architectures: source i386 amd64
     Origin: local-unstable
     Label: Local repository
     Components: main

   The reason for the "unstable" codename is that equivs will use it by default
   when building packages.

#. From the ``ubuntu/`` directory, import the package created before

   .. code:: console

     $ reprepro includedeb unstable ../ack-desktop_1.0_all.deb

   At the first import, ``reprepro`` will create the repository tree.

   Once the repository is set up, this is the only command that needs to be run
   again, when importing a new package or a new version for an existing package.


The repository is now ready to be used.

To make it available to all the machines, you can put host the ``ubuntu/`` tree
on on a machine running a web server, but if you already sync your files using
a service like Dropbox or OwnCloud, an easy solution is to just have the tree
synced by it. Since metapackages have no real content, they're very small.

All you need is to create a repository entry

.. code:: console

  $ echo "deb file:///home/ack/repo/ubuntu/ unstable main" | sudo tee /etc/apt/sources.list.d/local.list
  deb file:///home/ack/repo/ubuntu/ unstable main

with the correct path to the ``ubuntu/`` directory.

At this point, you can just install your package with ``apt``, and it will
automatically pull dependencies:

.. code:: console

  $ sudo apt update
  ...
  $ sudo apt install ack-desktop
