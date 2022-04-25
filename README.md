# ZYNQ Admin
## これはなに？
このツールはZYNQで動くLinuxのシステム管理をWeb経由で行えるようにするものです。

ZYNQ Linuxの時計、NTP同期、CPUの使用率、メモリ使用量、ディスク使用量などを見ることができ、boot.binの書き換えや再起動もできます。

[<img src="./doc/image1.png" alt="ZYNQ Adminの画面" width="320">](./doc/image1.png)

再利用がしやすいように、非常に質素なデザインとシンプルなJavaScriptで作られています。このWeb画面にお好みのCSSを適用したりして、お客様のシステムに組み込んで使ってください。

## 動作環境
Ubuntu 14.04LTS または Ubuntu 18.04LTSが動作しているZYNQ Linux

## インストール方法
このツールのインストール自体は難しくありません。/var/www/htmlフォルダに、このレポジトリをダウンロードするだけです。

```
cd /var/www/html
git clone https://github.com/tokuden/zynq-admin.git
```

## Apache2でCGIを有効にする
このシステムはCGIを使っているので、Apache2からCGIが動くようにしなければなりません。

まず、/etc/apache2/sites-available/000-default.conf を書き換えます。


CGIを実行するディレクトリには+ExecCgiの指定が必要です。また、AddHandlerで.cgiの拡張子がCGIであることを指示してください。
ディレクトリは環境に合わせて書き換えてください。


```
<VirtualHost *:80>
・・中略・・・
        DocumentRoot /var/www/html  ←環境に合わせて変更する
        <Directory /var/www/>  ←環境に合わせて変更する
            Options -Indexes +FollowSymLinks +MultiViews +ExecCgi  ←+ExecCgiを追加
            AllowOverride All
            Order allow,deny
            allow from all
        </Directory>

        AddHandler cgi-script .cgi .pl ←この行を追加
・・中略・・・
```

そして、
```
$ sudo a2enmod cgid
$ sudo systemctl restart apache2
```
でCGIを有効にしてApache2を再起動します。

## 管理パネルの表示

http://<ZYNQ LinuxのIPアドレス>/zynq-admin/
で、Web画面にシステム情報を表示することができます。

--------

# セットアップ
システム情報を表示するだけであれば、git cloneしてCGIを許可するだけ使えますが、ZYNQのシステムの設定を変更するには、CGIから管理者権限が必要なコマンドが使えるようにしなければなりません。そのためには設定ファイルをいくつか変更する必要があります。

## Webから再起動ができるようにする
Linuxの再起動は/sbin/rebootというプログラムで行われます。(Ubuntu 18ではrebootは/bin/systemctlへのシンボリックリンク)

rebootの実行にはroot権限が必要ですが、CGIで動くプログラムはwww-dataというユーザの権限で動くので、rebootをCGIから実行するためには、/etc/sudoersに記述を追加しなければなりません。以下、CGIからrebootを行うための方法を説明します。

## /etc/sudoersを書き換えて管理者コマンドをCGIから実行できるようにする

管理者以外の一般ユーザ(ApacheのCGIも含む)から管理者権限のコマンドを実行できるようにするには、/etc/sudoersにその旨を記載します。/etc/sudoersを直接書き換えることはせず、visudoというツールを使います。

使い方を誤ってsudoersを壊してしまうとシステム全体が使えなくなる危険があるので、注意深く作業してください。

まず、
`sudo visudo`
を実行して、/etc/sudoersを開きます。

書き換える場所は20行目付近にある、User privilege specificationの後の部分です。rootの後ろにwww-dataユーザ向けの追加をしてください。

```
# User privilege specification
root    ALL=(ALL:ALL) ALL
www-data ALL=(ALL:ALL) /sbin/reboot, /bin/systemctl, /bin/cp, /bin/hostname
```

です。

追加すべきコマンドは、

- /sbin/reboot ・・・ 再起動ができるようになる
- /bin/systemctl ・・・ サービスの開始/停止ができるようになる(Ubuntu18)
- /bin/cp ・・・ boot.binを始め、システムファイルを書き換えられるようになる
- /bin/hostname ・・・ ホスト名を変更できるようになる
- /bin/ping ・・・ PINGが打てるようになる(Ubuntu14)

なお、Ubuntu 18ではPingは管理者権限を必要としなくなったので追加する必要はなくなりました。

-----

# boot.binを更新できるようにする
ZYNQの起動ファイルは"boot.bin"で、このファイルはSDカードの第一パーティションに書き込まれています。しかし、boot.binを作るたびにSDカードを抜き差ししてWindows PCに挿すのは非常に手間がかかるので、ZYNQ LinuxからSDカードが見えるようにしてコマンドで書き換えられるようにしましょう。

まず、` sudo mkdir /mnt `で、/mntというフォルダを作り、ここにSDカードの第一パーティションをマウントします。起動時に自動的にマウントするように、/etc/fstabを編集します。

```
# UNCONFIGURED FSTAB FOR BASE SYSTEM
/dev/mmcblk0p1 /mnt vfat
```

これで、起動時に/mntフォルダにSDカードの第一パーティションがマウントされるようになります。


すが、このファイルは、通常はVivadoに含まれているbootgenというプログラムを使ってBitStreamにfsbl.elfとu-boot.elfを結合させて作ります。本プロジェクトにはbootgenのARM Linux版が含まれているので、Webフォーム上からBitStreamを送って、ZYNQ Linux上でboot.binを作り、SDカードを書き換えさせることが出来ます。





## NTPの同期ができるようにする
現在時刻のところにあるボタン「Sync」を押すと、サーバ上でntpdateというプログラムが走り、時刻を同期します。

ARM 32bit版 Ubuntu Linuxの14.04ではntpdateがありますが、Ubuntu 18.04にはデフォルトでは入っていません。Web上から時刻を同期するボタンを使えるようにするには、 ` apt install ntpdate ` でntpdateをインストールしておいてください。



