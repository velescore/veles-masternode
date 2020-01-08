ASSERT_TOOL_URL=https://raw.github.com/AltcoinBaggins/assert.sh/v1.1/assert.sh
SYSD_TOOL_URL=https://raw.githubusercontent.com/AltcoinBaggins/docker-systemctl-replacement/master/files/docker/systemctl.py
SCRIPT_URL=https://raw.githubusercontent.com/velescore/veles-masternode-install/master/masternode.sh
DAEMON_NAME=velesd

test_all:
	@make test_install
	@make test_env
	@make test_dns

test_install:
	@echo
	make check_dependencies
	@echo -n '[test_install] Running the masternode script ...'
	./install.sh install --non-interactive
	@echo "[test_install] Done [success]"

test_env:	
	make install_env_test_dependencies
	@echo -n '[test_env] Checking whether Veles Core daemon is running ... '
	@ps aux | grep -v grep | grep velesd > /dev/null && echo 'ok' || ( echo 'fail' ; exit 1 )
	@echo -n '[test_env] Testing internet connection and DNS ... '
	ping google.com -c 5 && echo 'ok' || ( echo -e "fail\n, DNS debug: " ; dig google.com ; exit 1 )
	@echo "[test_env] Done [success]"

test_dns:
	@echo -n '[test_dns] Checking DNS settings ...'
	@echo -n 'Checking /etc/systemd/resolved.conf ... '
	@if [ -f /etc/systemd/resolved.conf ]; then\
		grep "DNSStubListener=no" /etc/systemd/resolved.conf || ( echo 'fail' ; cat /etc/systemd/resolved.conf ; exit 1 );\
		grep "DNS=127\.0\.0\.1" /etc/systemd/resolved.conf || ( echo 'fail' ; cat /etc/systemd/resolved.conf ; exit 1 );\
		echo "ok";\
	else\
		echo "not present";\
	fi
	@echo -n 'Checking /etc/dnsmasq.conf ... '
	@if [ -f /etc/dnsmasq.conf ]; then\
		grep "port=53" /etc/dnsmasq.conf && ( echo 'fail' ; cat /etc/dnsmasq.conf ; exit 1 ) || echo "ok";\
	else\
		echo "not present";\
	fi
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
	@[ -f systemctl.py ] || wget --quiet $(SYSD_TOOL_URL) || exit 1
	@[ -x systemctl.py ] || chmod +x systemctl.py || exit 1
	@mv systemctl.py /usr/bin/systemctl || exit 1
	@[ -d "/etc/systemd/system" ] || mkdir -p "/etc/systemd/system" || exit 1

clean:
	echo "[test] Cleaning up ..."
	@rm assert.sh
	@rm assert.sh
