================================================
Full-disk encryption with Btrfs on Ubuntu Xenial
================================================

:date: 2016-04-23
:category: howto
:tags: btrfs, encryption, filesystem, ubuntu

Btrfs_ is a copy-on-write (CoW) filesystem
available in the standard Linux kernel, which provides advanced features like
snapshotting and volume management, similarly to what LVM_  provides.

I've been using `LVM` on my laptop for quite some time, to keep separate
volumes for filesystem root and ``/home``, and containers.  `LVM` makes this
easy and also allows to resize partitions without needing to move data.

Even though way more flexible than physical partitions, `LVM` volumes too have
a preallocated size; this can be a problem with many volumes and not a lot of
disk size (such as on laptops with SSDs). The choice is to either create small
partitions and grown them as needed (leaving empty space in the volume group),
or create larger partitions and possibly waste space.

In this regard `Btrfs` is much more flexible, since subvolumes use a global
space pool: a single partition can host multiple subvolumes that can be
created, destroyed, copied and snapshotted without wasting any unused space.
On the other hand, `Btrfs` volumes are not generic space pools, they can't be
used to host other filesystem types, so for instance for swap, a separate
partition is needed.

I decided to reinstall my laptop with the latest beta of Ubuntu 16.04 (which
has now been finalized and released), replacing the root and ``/home`` `LVM`
volumes with a single `Btrfs` partition and different subvolumes.

When reinstalling, I wanted to keep my full-disk encryption (FDE) setup, where
swap, root and ``/home`` partitions were encrypted, which I had on my previous
Wily installation (using the installer encrypted setup choice).

Unfortunately `FDE` with `Btrfs` is not available out-of-the-box in the
installer, since the "Encrypt the new Ubuntu installation for security" option
uses a single `Ext4` partition, but with a few manual steps during
installation, it's possible to have the same result using `Btrfs`.


Partitioning the disk
---------------------

The easiest way to do this is to use the disk configurator from the Ubuntu
installer:

#. boot the install media (DVD or USB stick), start the install and choose the
   *"Try ubuntu without installing"* option at boot

#. at the "Installation type" page, choose *"Something else"*

#. create 3 partitions of the following types:

   #. EFI system partition (for ``/boot/efi``). It can be quite small, since
      only a few MB will be used.
   #. Ext2 filesystem (for ``/boot``). This also doesn't need to be very big, a
      few hundred MB are enough.
   #. physical volume for encryption (for the `dm-crypt` volume), using the
      rest of the space. When selecting this option the installer will ask for
      an encryption password, which will be needed at each boot for unlocking
      the volume.

Now that we have physical partitions set up, we can quit the installer; we'll
restart after setting up volumes inside the last partition.

The next step is to create an LVM volume group in the encrypted partition, with
volumes for swap and root filesystem. Since the partition is ``/dev/sda3``
(we'll assume the target disk is ``/dev/sda``), the `dm-crypt` volume created
by the installer will be named ``/dev/mapper/sda3_crypt``.

Creating the LVM is just a few commands:

.. code:: console

  $ sudo vgcreate ubuntu /dev/mapper/sda3_crypt
  $ sudo lvcreate --name swap -L 16Gb ubuntu  # adjust size as needed
  $ sudo lvcreate --name root -l 100%FREE ubuntu


Installing Ubuntu
-----------------

At this point, we can launch the installer, selecting once again *"Something
else"* as installation type.

The disk partitioner will show the partitions we just created, we just need to
enable them with the proper mountpoint:

- ``/dev/sda1``: "EFI system partition", mounted on ``/boot/efi``
- ``/dev/sda2``: "Ext2 filesystem", mounted on ``/boot``
- ``/dev/mapper/ubuntu-root``: "Btrfs filesystem", mounted on ``/``
- ``/dev/mapper/ubuntu-swap``: "swap area"

Make sure that for all partitions (except swap) the "format" checkbox is
selected.

*IMPORTANT:* the physical device (``/dev/sda``) must be selected as target for
bootloader install.

Now we can proceed with the normal Ubuntu install, answering all configuration
questions as desired.

At the end of the installation process, *DO NOT REBOOT YET* (select "continue
testing").


Post-install setup
------------------

A few more manual steps are required after installing the system to make it
aware of the full-disk encryption setup. Since the partitioning has been done
manually, the installer didn't do it for us. All the following commands need to
be run as `root`:

mount the target root filesystem, and all pseudo-filesystems under it (to be
able to enter a ``chroot`` later)

.. code:: console

  # mount /dev/mapper/ubuntu-root /mnt -o subvol=@
  # mount -o bind /dev/ /mnt/dev
  # mount -t sysfs sysfs /mnt/sys
  # mount -t proc procfs /mnt/proc

get the ``UUID`` of the encrypted partition (*not* the ``PARTUUID``) and create
``/etc/crypttab`` in the target root

.. code:: console

  # blkid /dev/sda3
  /dev/sda3: UUID="<YOUR-UUID>" TYPE="crypto_LUKS" PARTUUID="f25a9621-045f-4d79-b0a0-489c5f7c0562"
  # echo "sda3_crypt UUID=<YOUR-UUID> none luks,discard" > /mnt/etc/crypttab

``chroot`` into the target root directory, to rebuild the kernel initramfs and
grub config

.. code:: console

  # chroot /mnt
  # mount /boot
  # mount /boot/efi
  # service lvm2-lvmetad start  # needed for grub to find the LVM volumes
  # update-initramfs -u
  # update-grub

Now everything should be set up, so we can undo all mounts, including the
target root filesystem.

.. code:: console

  # service lvm2-lvmetad stop
  # umount /boot/efi
  # umount /boot
  # umount /sys
  # umount /proc
  # umount /dev
  # exit  # from the chroot
  # umount /mnt

Done! Now we can reboot into the new system.

Before actually booting, a splash screen will ask the password to unlock the
encrypted volume (the one chosen when creating the partition).


Recap of partition setup
------------------------

The install uses three partitions, of which two get mounted directly:

.. code:: console

  $ mount | grep /dev/sda
  /dev/sda2 on /boot type ext2 (rw,relatime,block_validity,barrier,user_xattr,acl)
  /dev/sda1 on /boot/efi type vfat (rw,relatime,fmask=0077,dmask=0077,codepage=437,iocharset=iso8859-1,shortname=mixed,errors=remount-ro)

The encrypted ``/dev/sda3`` partition will be visible through the `dm-crypt`
volume:

.. code:: console

  $ sudo cryptsetup status /dev/mapper/sda3_crypt
  /dev/mapper/sda3_crypt is active and is in use.
    type:    LUKS1
    cipher:  aes-xts-plain64
    keysize: 512 bits
    device:  /dev/sda3
    offset:  4096 sectors
    size:    311025664 sectors
    mode:    read/write
    flags:   discards

Since the opened ``/dev/mapper/sda3_crypt`` volume contains an LVM setup, the
kernel automatically makes volumes inside it available:

.. code:: console

  $ sudo vgs
    VG     #PV #LV #SN Attr   VSize   VFree
    ubuntu   1   2   0 wz--n- 148.30g    0
  $ sudo lvs
    LV   VG     Attr       LSize   Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert
    root ubuntu -wi-ao---- 132.42g
    swap ubuntu -wi-ao----  15.88g

Finally, volumes in the `Btrfs` partition, ``/dev/mapper/ubuntu-root``, are
mounted. The installer automatically creates two subvolumes for ``/`` and
``/home``.

.. code:: console

  $ mount | grep /dev/mapper/ubuntu-root
  /dev/mapper/ubuntu-root on / type btrfs (rw,relatime,ssd,space_cache,subvolid=257,subvol=/@)
  /dev/mapper/ubuntu-root on /home type btrfs (rw,relatime,ssd,space_cache,subvolid=258,subvol=/@home)
  $ sudo btrfs subvolume list /
  ID 257 gen 16908 top level 5 path @
  ID 258 gen 16908 top level 5 path @home

Note that since the device is an `SSD`, `Btrfs` enables optimizations for it
(visible in the ``ssd`` mount option).


Additional subvolumes
---------------------

Arbitrary additional subvolumes can be created in the filesystem, even under
the root one. For example, tools like LXC_, LXD_, and Docker_ take advantage of
the Btrfs capabilities to store container filesystems and images in subvolumes,
so that they can be copied and snapshotted very quickly, without needing actual
data copy.

These are be listed among other subvolumes:

.. code:: console

   $ sudo btrfs subvolume list /
   ID 257 gen 16908 top level 5 path @
   ID 258 gen 16908 top level 5 path @home
   ID 343 gen 3691 top level 257 path var/cache/lxc/trusty/rootfs-amd64
   ID 348 gen 3811 top level 257 path var/lib/lxc/trusty/rootfs
   ID 562 gen 12995 top level 257 path var/lib/docker/btrfs/subvolumes/a1723918aa603a5c9d63bff2fc623ccbcc5ad1cbeb8c048929c65237ce61bebc
   ID 563 gen 12996 top level 257 path var/lib/docker/btrfs/subvolumes/e8eb5e7f51f415678c3126ca447e2df32d74fe041d0782bfb39357ae6cf28cec
   ID 581 gen 16882 top level 257 path var/lib/lxd/images/6cb0ba80a5fe32357568a473cbaf69f14d26da0ba6b08f5b1bcde7053fc73757.btrfs



.. _Btrfs: https://btrfs.wiki.kernel.org/
.. _LVM: https://en.wikipedia.org/wiki/Logical_Volume_Manager_(Linux)
.. _LXC: https://linuxcontainers.org/lxc/
.. _LXD: https://linuxcontainers.org/lxd/
.. _Docker: https://www.docker.com/
