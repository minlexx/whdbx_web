# Get python 3.6
If you already have python3.6, you don't have to install it,
check version:
```
python3 --version
```
If you already have python3.6, skip python installation and go directly to
[Install WHDBX section](INSTALL.md#install-whdbx).

If it does not say 3.6, you can try to install it:
```
sudo apt-get install python3.6
```
If your distro does not have python3.6, you can compile it from source:
* add deb-src lines
* install build dependencies
* clone git repo of cpython
* compile and install branch 3.6

Instructions below:

## add deb-src lines to /etc/apt/sources.list
add deb-src variants of existing deb-lines, needed for apt-get build-dep:
for each `deb http://` line add `deb-src http://...` variant:
```
sudo nano /etc/apt/sources.list
```
```
# example for ubuntu xenial:
deb http://archive.ubuntu.com/ubuntu/ xenial main
deb-src http://archive.ubuntu.com/ubuntu/ xenial main
```
```
# example for debian wheezy:
deb http://ftp.debian.org/debian wheezy main contrib non-free
deb-src http://ftp.debian.org/debian wheezy main contrib non-free
```
```
sudo apt-get update
```

## You will need git anyway:
```
sudo apt-get install git
```

## Build and install python 3.6
### Get dependencies for building python3
```
sudo apt-get install build-essential
sudo apt-get build-dep python3.2
```
### compile and install python 3.6
```
git clone https://github.com/python/cpython.git
cd cpython
git checkout -b 3.6 origin/3.6
mkdir build
cd build
../configure --prefix=/usr/local --enable-optimizations
make -j2
sudo make install
```

### install python requirements
```
/usr/local/bin/python3 -m pip install requests
/usr/local/bin/python3 -m pip install mako
/usr/local/bin/python3 -m pip install cherrypy
```

### create symbolic link for python3 in /usr/bin
```
cd /usr/bin
sudo ln -s /usr/local/bin/python3 python3
```

### now test that you actually have python3.6:
```
/usr/bin/python3 --version
```
You need to have at least 3.5 version to run!

# Install WHDBX:
## Create a user to run WHDBX web-app
```
sudo useradd -d /home/whdbx -m -N -s /bin/bash whdbx
```

## as whdbx user, clone whdbx repository
```
su whdbx
cd /home/whdbx
git clone https://github.com/minlexx/whdbx_web.git
cd whdbx_web
```
```
# create and edit local config:
cp whdbx_config.ini whdbx_config_local.ini
nano whdbx_config_local.ini
```
```
# verify that whdbx app can be launched at all, test:
chmod a+x main.py
./main.py --help
```

## Download eve database, 115 Mb from fuzzworks site
```
cd db
wget https://www.fuzzwork.co.uk/dump/latest/eve.db.bz2
bzip2 --decompress eve.db.bz2
```
```
# apply patches to db
sudo apt-get install sqlite3
cd sqlite_sql
chmod a+x update_database.sh
./update_database.sh
cd ../../
```

# test pure web app, without nginx
```
./main.py --host 0.0.0.0 --port 8080
```

Now go to your http://ip_address:8080/ and test.

# Install nginx
```
sudo apt-get install nginx
```
Configuring nginx is a bit out of scope for this guide.

## Configure nginx as reverse-proxy
This guide from CherryPy (deploy section) is pretty good:
http://docs.cherrypy.org/en/latest/deploy.html#id4

## Configure SSL hosting and letsencrypt certificate
You need to install certbot and do:
```
certbot --nginx
```

### My final nginx site config looks like this:
```
upstream apps {
        server 127.0.0.1:8081;
}


server {
        listen 80;
        listen 443 ssl;
        server_name wh.minlexx.ru;

        access_log /home/whdbx/whdbx_web/logs/access.log combined;
        error_log /home/whdbx/whdbx_web/logs/error.log;

        location ^~ /static/ {
                root /home/whdbx/whdbx_web/;
        }

        location / {
                proxy_pass http://apps;
                proxy_redirect off;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Host $server_name;
        }

        location ~ /\.ht {
                deny all;
        }

        ssl_certificate /etc/letsencrypt/live/wh.minlexx.ru/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/wh.minlexx.ru/privkey.pem; # managed by Certbot
        include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
        ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot

        if ($scheme != "https") {
                return 301 https://$host$request_uri;
        } # managed by Certbot
}
```

# (Optional) install redis, redis-py and configure sessions
```
sudo apt-get install redis-server
/usr/local/bin/python3 -m pip install redispy
```
Edit `whdbx_config_local.ini`: set `session_storage_type = redis`.
Default values should be enough to work.