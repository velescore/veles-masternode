Contributing to Veles Masternode
================================

The Veles Masternode project operates an open contributor model where anyone is
welcome to contribute towards development in the form of peer review, testing
and patches. The codebase is maintained using the "contributor workflow"
where everyone without exception contributes patch proposals using 
"pull requests". This facilitates social contribution, easy testing and peer review.

Development of Veles Masternode follows the same guidelines does the Veles Core,
hence **this document should be understood as an extension of the document
[Contributing to Veles Core](https://github.com/velescore/veles/blob/master/CONTRIBUTING.md)**, 
which explains the practical process and guidelines for contributing.


Guidelines specific for Veles Masternode contribution
=====================================================
Parts of the document [Contributing to Veles Core](https://github.com/velescore/veles/blob/master/CONTRIBUTING.md)**
that are too project-specific are over-ruled by their Veles Masternode equivalents listed below.


### Contributor Workflow
...
The title of the pull request should be prefixed by the component or area that
the pull request affects. Valid areas are:

  - `service` for changes to service definitions or proccess control
  - `config` for changes to the configuration files
  - `vpn` for changes related to the VPN / dVPN service
  - `httpd` for changes to the HTTP daemon excluding API changes
  - `api` for changes to the masternode JSON API
  
Valid are also all the areas listed in the original document. Those are (if not stated otherwise
    in the latest version of document):
    
  - `consensus` for changes to consensus critical code
  - `doc` for changes to the documentation
  - `qt` or `gui` for changes to veles-qt
  - `log` for changes to log messages
  - `mining` for changes to the mining code
  - `net` or `p2p` for changes to the peer-to-peer network code
  - `refactor` for structural changes that do not change behavior
  - `rpc`, `rest` or `zmq` for changes to the RPC, REST or ZMQ APIs
  - `script` for changes to the scripts and tools
  - `test` for changes to the Veles unit tests or QA tests
  - `util` or `lib` for changes to the utils or libraries
  - `wallet` for changes to the wallet code
  - `build` for changes to the GNU Autotools, reproducible builds or CI code
  - `mn` for changes to the masternode or governance code


Copyright
---------

By contributing to this repository, you agree to license your work under the 
GNU/GPL license unless specified otherwise at the top of the file itself. 
Any work contributed where you are not the original 
author must contain its license header with the original author(s) and source.
