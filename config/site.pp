node default {
   package { 'epel-release':
   ensure => 'installed',
   }

   #package { "ntp":
   #ensure => installed,
   #require => Package['epel-release'],
   #}

   package { "telnet":
   ensure => installed,
   require => Package['epel-release'],
   }

   package { "mtr":
   ensure => installed,
   require => Package['epel-release'],
   }

   package { "tree":
   ensure => installed,
   require => Package['epel-release'],
   }

   class { 'ntp':
   servers => [ '0.us.pool.ntp.org iburst','1.us.pool.ntp.org iburst','2.us.pool.ntp.org iburst','3.us.pool.ntp.org iburst'],
   }

}
