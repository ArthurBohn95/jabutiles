These are all the required steps to setup the environment on the Steam Deck to run all the code in this repo.



# 1. Distrobox

``` bash
distrobox create -n <container_name> -i ubuntu:22.04 or newer
distrobox enter <container_name>
```

After the container exists, some basic software needs to be installed:



# 2. Git

Reference: https://www.digitalocean.com/community/tutorials/how-to-install-git-on-ubuntu

``` bash
sudo apt update
sudo apt install git -y
```

Test with:

``` bash
git --version
```



# 3. VS Code

Reference: https://code.visualstudio.com/docs/setup/linux

``` bash
sudo apt-get install wget gpg
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" |sudo tee /etc/apt/sources.list.d/vscode.list > /dev/null
rm -f packages.microsoft.gpg

sudo apt install apt-transport-https
sudo apt update
sudo apt install code -y
```

Test with:

``` bash
code --version
```



## 3.1 Useful extensions

- Material Icon Theme
- Indent Rainbow
- Markdown Preview Github
- Gif Player



# 4. Python 3.12

Reference: https://www.linuxtuto.com/how-to-install-python-3-12-on-ubuntu-22-04/

``` bash
sudo apt update
sudo apt upgrade -y
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
# You have to click ENTER
```

``` bash
sudo apt update
sudo apt install python3.12
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12
sudo apt install python3.12-dev python3.12-venv
```



## 4.1. Venv creation

Reference: https://stackoverflow.com/questions/77230254/cannot-properly-create-a-virtual-enviroment-in-python-3-12

``` bash
python3.12 -m venv venv
```

Test with:

```bash
. venv/bin/activate
```



## 4.2. Installing Arcade

Reference: https://pypi.org/project/arcade/

```bash
. venv/bin/activate
pip install arcade
```

Test with:

```bash
python -m arcade.examples.sprite_explosion_bitmapped
```



## 4.3. Installing dependencies

``` bash
pip install pillow numpy
```



## 4.4. Installing Blender dependencies

References:  
https://pypi.org/project/PyGObject/  
https://pypi.org/project/bpy/

``` bash
. venv/bin/activate
pip install PyGObject bpy
```





# 5. Additional references

## 5.1. Blender

- https://blenderartists.org/t/rendering-automation-automated-image-resource-change-automated-camera-change/1476203/2

- https://www.reddit.com/r/blenderhelp/comments/rbjale/how_do_i_make_a_plane_transparent_when_rendering/


