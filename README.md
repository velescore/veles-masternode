Veles Masternode integration/staging tree
=========================================
![Master Build Status](https://img.shields.io/travis/velescore/veles-masternode/master?style=for-the-badge) ![Latest Release](https://img.shields.io/static/v1?label=Release&message=unreleased&color=blue&style=for-the-badge) ![Licence](https://img.shields.io/github/license/velescore/masternode-installer?color=blue&style=for-the-badge)    

https://veles.network

About Veles
------------
Veles Core is an open-source blockchain ecosystem providing services such as decentralized VPN in order to help people to defend their online privacy and free access to an information. 
Backed by unique blockchain with features such dynamic block rewards and halving schedule, independent multi-algo PoW consensus, protected against common issues such as 51% attacks. Designed as multi-tiered network which builds on the concept of self-incentivized Masternodes which provide robust service and governance layer.

Veles Masternode Gen 2
----------------------
This is master branch of Veles Masternode 2nd generation, latest development version. The stable release can be installed using [Veles Masternode Gen 1 Installer](https://github.com/velescore/masternode-installer). For a core wallet and blockchain node refer to [Veles Core](https://github.com/velescore/veles) repository. This package provides full implementation of Veles Masternode with robust service layer designed to run dapps such as dVPN, proccess manager and installation wizard.

Installation Instructions and Notes
-----------------------------------
Installation is currently only supported on Ubuntu 18.04 LTS (Bionic Beaver) and Ubuntu 19.04 (Disco Dingo).

1.  Clone the repository

        https://github.com/velescore/veles-masternode

2.  Run the installation wizard
        
        veles-masternode/install.sh

### Linux (Ubuntu) Notes
1.  Update your package index

        sudo apt-get update

### Windows (64/32 bit) Notes
Veles Masternode is currently not supported on Windows platform


License
-------
Veles Masternode is released under the terms of the GNU/GPL license v3. See [COPYING](COPYING)
and [LICENSE](LICENSE) for more information or see https://opensource.org/licenses/GPL-3.0 .

Development Process
-------------------
The `master` branch is regularly built and tested, but is not guaranteed to be
completely stable. [Tags](https://github.com/velescore/veles-masternode/tags) will be created
regularly to indicate new official, stable release versions of Veles Core.

The contribution workflow is described in [CONTRIBUTING.md](CONTRIBUTING.md).

Testing
-------
Testing and code review is the bottleneck for development; we get more pull
requests than we can review and test on short notice. Please be patient and help out by testing
other people's pull requests, and remember this is a security-critical project where any mistake might cost people
lots of money.

### Automated Testing
The Travis CI system makes sure that every pull request is built currently for Ubuntu 18.04 LTS "Bionic Beaver" and Ubuntu 19.04 "Disco Dingo", and that unit/sanity tests are run automatically.

