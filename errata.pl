#!/usr/bin/perl

use strict;
use warnings;

use English;

use LWP::UserAgent;
use LWP::ConnCache;
use Frontier::Client;
use Getopt::Long;
use Data::Dumper;
use Date::Manip;
use File::Temp qw/tempdir/;
use File::Spec;
use File::stat;
use Digest::MD5 qw/md5_hex/;

my $host = 'rhn.redhat.com';
my $proxy;
my $user;
my $password;
my $channel_label;
my $package_label;
my $directory;
my $download = 1;
my $timestamp = 0;
my $since = '1970-01-01';
my $limit = 3;
my $max_errors = 0;
my $help = 0;
my $rhnlogin = 'https://www.redhat.com/wapps/sso/login.html';

my $help_message = "Usage: $PROGRAM_NAME --user=<user> --password=<password> --channel=<channel_label> [ --package=<package_name> ] [ --directory=<target_directory> ] [ --host=<hostname> ] [ --proxy=<proxy_host[:proxy_port]> ] [ --limit=<max_packages> ] [ --max-errors=<max_errors> ] [ --since=<YYYY-MM-DD> ] [ --nodownload ] [ --timestamp ]\n";
my $no_user_message = "I need a username and password.\n\n" . $help_message;

my $result = GetOptions ("host=s"       => \$host,
			 "proxy=s"      => \$proxy,
			 "user=s"       => \$user,
			 "password=s"   => \$password,
			 "channel=s"    => \$channel_label,
			 "package=s"    => \$package_label,
			 "directory=s"  => \$directory,
			 "download!"    => \$download,
			 "timestamp"    => \$timestamp,
			 "since=s"      => \$since,
			 "limit=i"      => \$limit,
			 "max-errors=i" => \$max_errors,
                         "help"         => \$help);

die $help_message if $help;

my $errors = 0;

die "No host!\n\n" . $help_message unless $host;

my $client = new Frontier::Client('url' => "https://$host/rpc/api",
                                  'proxy' => $proxy);

my $apiver = $client->call('api.system_version');
print "$host is running API version $apiver.\n\n";

if (! $user) {
  print "User login to check? ";
  chomp($user = <STDIN>);
}

die $no_user_message unless $user;

if (! $password) {
  print "Password? ";
  system "stty -echo";
  chomp($password = <STDIN>);
  system "stty echo";
  print "\n\n";
}

die $no_user_message unless $password;
my $session;

eval {
  $session = $client->call('auth.login', $user, $password);
};

if ($EVAL_ERROR or ! $session) {
  die "Unable to login.\n\n" . $help_message;
}

print "Logged in via API.\n\n";

if (! $channel_label) {
  print "Listing all channels...\n";
  my $channels = $client->call('channel.listSoftwareChannels', $session);

  foreach my $channel (@$channels) {
    printf("%s\n", $channel->{channel_label});
  }

  print "Consult the above output for the Channel *label* to list all packages from [e.g. rhel-i386-server-5 , rhel-i386-as-4-extras] ? ";
  chomp($channel_label = <STDIN>);
}

die "No channel label given.\n\n" . $help_message unless $channel_label;

print "Fetching latest package information for channel $channel_label...\n\n";

my $packages = $client->call('channel.software.listLatestPackages', $session, $channel_label);

if ($package_label) {
  $limit = 1;
}

print "Found " . scalar @{$packages} . " packages (limit is set to $limit).\n\n";

my %pkg_info;
my $package_count = 0;
my $package_detail = 0;

$OUTPUT_AUTOFLUSH = 1;

my $since_secs = UnixDate(ParseDate($since), "%s");

if ($package_label or $download or $timestamp or $since_secs > -7200) {
  if ($package_label) {
    print "Looking for $package_label from " . scalar @{$packages} . " packages:\t";
  } else {
    my $pkgs = $limit < scalar(@{$packages}) ? $limit : scalar(@{$packages});
    print "Fetching details for $pkgs packages:\t";
  }
  foreach my $package (@{$packages}) {
    $package_count++;
    if (not $package_label and $limit and $package_count > $limit) {
      last;
    }
    print "\r\t\t\t\t\t\t\t\t\t" . $package_count;
    if (not $package_label or $package_label eq $package->{package_name})
    {
      my $pkg_details = $client->call('packages.getDetails', $session, $package->{package_id});
      $pkg_info{$package->{package_id}."mtime"} = $pkg_details->{package_last_modified_date};
      $pkg_info{$package->{package_id}."md5sum"} = $pkg_details->{package_md5sum};
      $package_detail++;
    }
  }
  print "\n\n";
}

$client->call('auth.logout', $session);

if ($package_label and $package_detail eq 0) {
  print "Package $package_label not found from channel $channel_label!\n\n";
  exit 1;
}

print "Logging in via WWW...\n\n";

my $ua = new LWP::UserAgent;
$ua->proxy(['http', 'https'], $proxy) if (defined $proxy);
$ua->cookie_jar({});
$ua->conn_cache(new LWP::ConnCache);

# For wget
if (defined $proxy) {
  $ENV{http_proxy} = $proxy;
  $ENV{https_proxy} = $proxy;
}

# Ignore cookie warnings
local $SIG{__WARN__} = sub {
  warn @_ unless $_[0] =~ m(^.* too (?:big|small));
};

my $request = HTTP::Request->new(GET => $rhnlogin);
my $response = $ua->request($request);
$response = $ua->post($rhnlogin,
  [
   'username' => $user,
   'password' => $password,
   '_flowId'  => "legacy-login-flow"
 ]
);

if (not $directory) {
  $directory = setup_temp_dir();
}

if ($download) {
  print "Downloading to $directory.\n\n";
  chdir($directory) or die "Could not go to: $directory";
} else {
  print "Available packages on channel ${channel_label}:\n\n";
}

$package_count = 0;
my $download_count = 0;
my $download_filename;

foreach my $package (@{$packages}) {
  if ($package_label and $package_label ne $package->{package_name}) {
    next;
  }

  $package_count++;

  if (not $package_label and $limit and $package_count > $limit) {
    --$package_count;
    last;
  }

  # Skip older packages than asked if downloading
  my $pkg_secs = UnixDate(ParseDate($pkg_info{$package->{package_id}."mtime"}), "%s");
  if ($since_secs > -7200) {
    if ($download and (not $pkg_secs or $since_secs > $pkg_secs)) {
      print "Skipping $package->{package_name} (older than $since).\n";
      next;
    }
  }

  my $md5_sum = $pkg_info{$package->{package_id}."md5sum"};
  my $download_filename = $package->{package_name} . "-" . $package->{package_version} . "-" . $package->{package_release} . "." . $package->{package_arch_label} . ".rpm";

  if ($download) {
    print "Downloading $download_filename... ";
    if (-e $download_filename and $md5_sum) {
      open FH, $download_filename or die "Could not open $download_filename for reading: $OS_ERROR";
      binmode(FH);
      my $existing_rpm;
      my $buffer;
      while (read FH, $buffer, 8*2**10) {
	$existing_rpm .= $buffer;
      }
      close FH;
      if (md5_hex($existing_rpm) eq $md5_sum) {
	print "already exists.  Skipping.\n";

        if ($timestamp) {
          utime $pkg_secs, $pkg_secs, $download_filename;
        }

	next;
      }
    }
  }

  my $path = '/rhn/software/packages/details/Overview.do?pid=' . $package->{package_id};
  $request = HTTP::Request->new(GET => "https://" . $host . $path);
  $response = $ua->request($request);
  $response = $ua->post("https://" . $host . $path);

  if ($response->is_error()) {
    print "Could not get https://${host}${path}\n";
    print "Error: " . $response->status_line . "\n";
    if (++$errors > $max_errors) {
      die "Exiting on error $errors.\n";
    }
    next;
  }

  my $download_url;

  if ($response->as_string =~ m|"(https://[\w\.-]*redhat.com/rhn/.*/[^"]*)">Download Package|) {
    $download_url = $1;
    $download_url =~ m|.*/(.*)$|;
    $download_filename = $1;
    $download_filename =~ s/\?.*$//;
    # Needed if no details fetched earlier
    if ($response->as_string =~ m|MD5 Sum:.*<td><tt>(\w+)</tt>|s) {
      $md5_sum = $1;
    }
  } else {
    warn "Could not find download link at https://${host}${path}\n";
    if (++$errors > $max_errors) {
      die "Exiting on error $errors.\n";
    }
    next;
  }

  if ($download) {
    # Use wget for better proxy support and to get timestamps right
    my $cmd = "wget -q \"$download_url\" -O \"$download_filename\"";
    system($cmd);
    if ($? ne 0) {
        print "\n  Could not wget ${download_url}\n";
        print "  Error: " . $? . "\n";
        if (++$errors > $max_errors) {
            die "Exiting on error $errors.\n";
        }
        next;
    }

    # Check the result
    open FH, $download_filename or die "Could not open $download_filename for reading: $OS_ERROR";
    binmode(FH);
    my $existing_rpm;
    my $buffer;
    while (read FH, $buffer, 8*2**10) {
        $existing_rpm .= $buffer;
    }
    close FH;
    if (md5_hex($existing_rpm) ne $md5_sum) {
        print "failed: MD5Sum mismatch!\n";
	next;
    }

    $download_count++;

    if ($timestamp) {
      utime $pkg_secs, $pkg_secs, $download_filename;
    }

    print "done.\n";
  } else {
    print "Package: " . $download_filename . "\n";
    print " MD5Sum: " . $md5_sum . "\n";
    print "    URL: " . $download_url . "\n\n";
  }
}

$OUTPUT_AUTOFLUSH = 0;

print "\nProcessed " . $package_count . " packages, $download_count downloaded.\n";
if ($download_count) {
  print "\nDownloaded packages are available in $directory.\n";
}

sub setup_temp_dir {
  my $dir = tempdir(CLEANUP => 0);
  my ($volume,$directories,$file) = File::Spec->splitpath($dir, 1);
  my $target = File::Spec->catdir($directories, "repo");

  $dir = File::Spec->catpath($volume, $target, '');
  mkdir $dir;

  return $dir;
}
