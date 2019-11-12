#!/bin/bash

echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf
echo "net.ipv6.conf.default.disable_ipv6 = 1" >> /etc/sysctl.conf
sysctl -p

export PATH=/opt/puppetlabs/bin:$PATH
puppet apply --modulepath=/etc/puppetlabs/code/environments/production/modules /home/ec2-user/HelloAfterpay/config/site.pp
