#!/bin/bash

echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf
echo "net.ipv6.conf.default.disable_ipv6 = 1" >> /etc/sysctl.conf
echo "fs.file-max=65535" >>  /etc/sysctl.conf
sysctl -p

export PATH=/opt/puppetlabs/bin:$PATH
mv /home/ec2-user/HelloAfterpay/config/site.pp /etc/puppetlabs/code/environments/production/manifests/
puppet apply --modulepath=/etc/puppetlabs/code/environments/production/modules /etc/puppetlabs/code/environments/production/manifests/site.pp
