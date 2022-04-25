#!/usr/bin/perl

use MIME::Base64;
use File::Basename;

#送信されたデータを受け取る
if ($ENV{'REQUEST_METHOD'} eq 'POST') {
  read(STDIN, $alldata, $ENV{'CONTENT_LENGTH'});
} else {
  $alldata = $ENV{'QUERY_STRING'};
}

foreach $data (split(/&/, $ENV{'QUERY_STRING'})) {
  ($key, $value) = split(/=/, $data);

  $value =~ s/\+/ /g;
  $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack('C', hex($1))/eg;
  $value =~ s/\t//g;
  $in{"$key"} = $value;
}

my ($sec, $min, $hour, $mday, $mon, $year);
($sec, $min, $hour, $mday, $mon, $year) = localtime($in{'lastModified'});
$year += 1900;
$mon += 1;

print "Content-Type: text/plain; charset=UTF-8\n\n";


if ($in{'filename'} eq '') {
	print "ファイル名が空です";
	exit;
}

print "ファイル名は $in{'filename'} です。<br>";
print "ファイルの日付は";
printf("%04d/%02d/%02d %02d:%02d:%02d\n", $year ,$mon, $mday, $hour, $min, $sec);
print "です。<br>";
$tmpfile = "/var/tmp/$in{'filename'}";
open(OUT, "> $tmpfile");
binmode OUT;
$data = $in{'formData'};
print(OUT $alldata);
close(OUT);
utime $in{'lastModified'}, $in{'lastModified'}, "$tmpfile";
chmod 0666, "$tmpfile";

my ($base_name, $dir, $suffix) = fileparse($in{'filename'}, '.bin');
if ($suffix eq '.bin') {
	my $file_size = -s "/var/tmp/$in{'filename'}";
	print "保存したファイルサイズは $file_size です。";
	system("echo $in{'password'} | sudo -S cp -p $tmpfile /mnt/boot.bin");
	print "/mnt/boot.binにコピーしました";
}

my ($base_name, $dir, $suffix) = fileparse($in{'filename'}, '.bit');
if ($suffix eq '.bit') {
	my $biffile = "/var/tmp/bootimage.bif";
	open(OUT, "> $biffile");
	print(OUT "the_ROM_image:\n");
	print(OUT "{\n");
	print(OUT "        [bootloader]/home/share/fsbl.elf\n");
	print(OUT "        $tmpfile\n");
	print(OUT "        /home/share/u-boot.elf\n");
	print(OUT "}\n");
	close(OUT);
	print("------boot.binを生成します------\n");
	system("/home/share/bootgen -w -image /var/tmp/bootimage.bif -o i /home/share/boot.bin 2>&1");
	system("ls -altr /home/share/boot.bin");
	print("------/mntにコピーします------\n");
	system("echo $in{'password'} | sudo -S cp -p /home/share/boot.bin /mnt/boot.bin 2>&1");
	print("------/mntの状況------\n");
	system("ls -altr /mnt/boot.bin");
	unlink $biffile;
}

unlink "/var/tmp/$in{'filename'}";
exit;
