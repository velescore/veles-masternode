ASSERT_TOOL_URL=https://raw.github.com/AltcoinBaggins/assert.sh/v1.1/assert.sh
SYSD_TOOL_URL=https://raw.githubusercontent.com/AltcoinBaggins/docker-systemctl-replacement/master/files/docker/systemctl.py
SCRIPT_URL=https://raw.githubusercontent.com/velescore/veles-masternode-install/master/masternode.sh
DAEMON_NAME=velesd

PACKAGE_DIR := $(shell pwd -P)
DATA_DIR := $(shell echo "${PACKAGE_DIR}/data")
ROOT_PREFIX := /
DIST_PREFIX := $(shell echo "${DATA_DIR}/dist")
LOG_FILE := /tmp/velesmn-install.log
CORE_RELEASE_URL := https://github.com/velescore/veles/releases/download/v0.18.1.3/veles-0.18.1.3-generic-linux-amd64.tar.gz
CORE_RELEASE_DIR := veles-linux-amd64

export PACKAGE_DIR
export DATA_DIR
export ROOT_PREFIX
export DIST_PREFIX
export LOG_FILE
export CORE_RELEASE_URL
export CORE_RELEASE_DIR

install:
	@if [[ "$(DEBUG)" == "" ]] ; then bin/installer install; else bin/installer "$(DEBUG)"; fi 

auto_install:
	bin/installer install --non-interactive

test_all:
	@make test_install
	@make test_env
	@make test_dns

test_install:
	@echo
	make check_dependencies
	@echo -n '[test_install] Running the masternode script ...'
	make auto_install
	@echo "[test_install] Done [success]"

test_env:	
	make install_env_test_dependencies
	@echo -n '[test_env] Checking whether Veles Core daemon is running ... '
	@ps aux | grep -v grep | grep velesd > /dev/null && echo 'ok' || ( echo 'fail' ; exit 1 )
	@echo -n '[test_env] Testing internet connection and DNS resolution ... '
	ping veles.network -c 5 && echo 'ok' || ( echo -e "fail\n, DNS debug: " ; dig google.com ; exit 1 )
	@echo "[test_env] Done [success]"

test_dns:
	@echo -n '[test_dns] Testing DNS server ...'
	nslookup veles.network 10.100.0.1
	@echo "[test_dns] Done [success]"

docker_test_all:
	@make install_docker_systemd
	@echo -e "[docker_test_install] Preparing the testing evironment ... "
	@make test_all
	@echo -e "[docker_test_install] Done [success] \n"

check_dependencies:
	@echo '[check_dependencies] Starting the test ...'
	@echo -n "Checking whether ifconfig command is present ... "
	@command -v ifconfig >/dev/null 2>&1  && echo "yes" || echo "no"
	@echo -n "Checking whether ip command is present ... "
	@command -v ip >/dev/null 2>&1  && echo "yes" || echo "no"
	@echo -n "Checking whether netstat command is present ... "
	@command -v netstat >/dev/null 2>&1  && echo "yes" || echo "no"
	@echo -n "Checking whether curl command is present ... "
	@command -v curl >/dev/null 2>&1  && echo "yes" || echo "no"
	@echo -n "Checking whether wget command is present ... "
	@command -v wget >/dev/null 2>&1  && echo "yes" || echo "no"
	@echo -n "Checking whether sed command is present ... "
	@command -v sed >/dev/null 2>&1  && echo "yes" || echo "no"
	@echo -n "Checking whether awk command is present ... "
	@command -v awk >/dev/null 2>&1  && echo "yes" || echo "no"
	@echo -n "Checking whether basename command is present ... "
	@command -v basename >/dev/null 2>&1  && echo "yes" || echo "no"
	@echo -n "Checking whether apt-get package manager is present ... "
	@command -v apt-get >/dev/null 2>&1  && echo "yes" || echo "no"
	@echo -n "Checking whether yum package manager is present ... "
	@command -v yum >/dev/null 2>&1  && echo "yes" || echo "no"
	@echo -n "Checking whether systemd is installed ... "
	@command -v systemctl >/dev/null 2>&1  && echo 'yes' || (echo "no, but is required!" ; exit 1)
	@echo -e "[check_dependencies] Done [success] \n"

install_env_test_dependencies:
	@echo '[test] Installing assertion toolkit ...'
	@[ -f assert.sh ] || wget --quiet $(ASSERT_TOOL_URL) || exit 1
	@[ -x assert.sh ] || chmod +x assert.sh || exit 1
	@echo '[test] Installing iputils-ping ... '
	@apt-get update
	@apt-get install iputils-ping -y

install_docker_systemd:
	@echo '[test] Installing custom Docker systemd ...'
	@apt-get update
	@apt-get install -qy docker wget python
	@[ -f systemctl.py ] || wget --quiet $(SYSD_TOOL_URL) || exit 1
	@[ -x systemctl.py ] || chmod +x systemctl.py || exit 1
	@mv systemctl.py /usr/bin/systemctl || exit 1
	@[ -d "/etc/systemd/system" ] || mkdir -p "/etc/systemd/system" || exit 1

clean:
	echo "[test] Cleaning up ..."
	@rm assert.sh
	@rm assert.sh
