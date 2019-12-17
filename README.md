Veles Masternode integration/staging tree
=========================================
![Licence](https://img.shields.io/static/v1?label=License&message=GPL-3.0&color=green&style=for-the-badge)   ![Latest Release](https://img.shields.io/static/v1?label=Release&message=unreleased&color=blue&style=for-the-badge)

https://veles.network

About Veles
------------
Veles Core is open-source software project dedicated to development of technologies focused on privacy and freedom of access to an information, such as decentralized VPN provided by multi-tiered self-incentivized p2p network. Backed by custom blockchain that aims to overcome common issues
associated with popular blockchains, such as 51% attack resistance, multiple PoW algorithms or dynamic block reward and halving system. Visit [Veles Core repository](https://github.com/velescore/veles) for more information.

About Masternodes
-----------------
Veles Masternodes are a backbone for multi-tiered Veles Network. Masternode is a dedicated Veles blockchain node (backed by monetary deposit 
as a countermeasure against misuse) rewarded by the network consensus for reliably providing decentralized services. 

Veles Masternode 2.0 [development/testing]
------------------------------------------
This is master branch of Veles Masternode generation 2, which is currently in development/testing until official release into production during Q1 2020, when Masternodes generation 1 will bephased out. (For current stable Veles Masternode implementation visit [Veles Masternode Installer](https://github.com/velescore/masternode-installer) to install Masternode gen 1.0.).This package provides full implementation of Veles Masternode with robust service layer designed to run dapps such as dVPN, including proccess manager and installation wizard.


Installation Instructions and Notes
-----------------------------
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
