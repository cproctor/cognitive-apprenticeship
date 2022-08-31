# Cognitive Apprenticeship

Cognitive Apprenticeship is an app which implements a toy academic journal 
for an introductory PhD seminar.

## Deployment

### Prepare virtual machine

Create a new VM running Ubuntu 22.04 (Digital Ocean Droplet) with SSH keys.
Ensure that domains are using DO's nameservers (`ns{1,2,3}.digitalocean.com`)
and that DO is routing domains to the droplet.
SSH in as root.

```
apt update
apt upgrade
apt install certbot nginx gh python3.10-venv tree
adduser chris
usermod -aG sudo chris
mv .ssh /home/chris/.ssh
chown -R chris:chris /home/chris/.ssh
sudo ufw allow OpenSSH
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
exit
```

Create a personal access token in [github](https://github.com/settings/tokens).
SSH in as chris and save the token in `~/github.txt`.

```
gh auth login --with-token < ~/github.txt
gh auth setup-git
export GITHUB_TOKEN="$(cat ~/github.txt)"
sudo chown -R chris:chris /opt
cd /opt
mkdir -p lai615/logs lai615/static_root
cd lai615
gh repo clone cproctor/cognitive-apprenticeship
cd /opt
gh repo clone cproctor/async_course
```

Configure app settings. 

```
cd /opt/lai615/cognitive-apprenticeship/cognitive_apprenticeship/
```

- Generate secret key
  ```
  from django.core.management.utils import get_random_secret_key  
  get_random_secret_key()
  ```
- `ALLOWED_HOSTS=['localhost', 'cisljournal.net']`
- `STATIC_ROOT="/opt/lai615/static_root"`
- Configure logging (`cognitive_apprenticeship/deploy/settings_logging.py`)

Install dependencies

```
python3 -m venv /opt/lai615/env
source /opt/lai615/env/bin/activate
cd /opt/lai615/cognitive-apprenticeship/
pip install -r requirements.txt
```

Setup tasks

```
./manage.py collectstatic
./manage.py migrate
deactivate
```

### Services

```
cd /opt/lai615/cognitive-apprenticeship/cognitive_apprenticeship/deploy
sudo cp gunicorn615.socket gunicorn615.service /etc/systemd/system/
sudo chown -R www-data:www-data /opt/lai615
sudo systemctl start gunicorn615
sudo systemctl status gunicorn615
```

### Networking

```
sudo cp nginx.conf /etc/nginx/nginx.conf
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl status nginx
```


- Set debug to False
