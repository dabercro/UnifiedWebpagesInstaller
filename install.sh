#!/bin/bash

# This is an installer used to install the ShowLogs webpage on your very own AFS space on lxplus.
# Yes, it only works there.
# This is in case you want me to make changes to my own page but I don't like you or something.

installName=$1

# Get desired installation name from the user.

if [ "$installName" = "" ]
then
    echo ""
    echo "Usage: $0 <INSTALL_NAME>"
    echo ""
    echo "Use one argument to give a name to the service you would like to install to show the unified logs."
    echo ""
    exit 0
fi

# If the spot is not free, don't use it.

if [ -d ~/www/$installName -o -f ~/www/$installName ]
then
    # Blatant ripoff from Homebrew because that message is funny.
    echo "~/www/$installName already exists. Cowardly refusing to touch it."
    exit 0
fi
if [ -f ~/www/cgi-bin/$installName.fcgi ]
then
    echo "~/www/cgi-bin/$installName.fcgi already exists. Cowardly refusing to touch it."
    exit 0
fi

# Get the location of user and the template files before I wonder off

whereAmI=`pwd`
fileLoc=`dirname $0`

# Initialize Django project.

cd ~/www

# Look for django installation
adminCommand=`which django-admin.py`
if [ "$adminCommand" = "" ]
then
    adminCommand=`which django-admin`
fi
if [ "$adminCommand" = "" ]
then
    # If it can't be found, time to install
    # This is mostly straight from the AFS page, so that should be safe, right?

    wget https://www.djangoproject.com/m/releases/1.6/Django-1.6.5.tar.gz
    tar -zxvf Django-1.6.5.tar.gz
    mv Django-1.6.5 django

    # Now I'm making up stuff
    cd django
    python2.6 setup.py install --prefix=~/.local
    PATH=$PATH:~/.local/bin
    adminCommand=`which django-admin.py`

    if [ "$adminCommand" = "" ]
    then
        echo "This script did not work as I was expecting..."
        echo "Get django-admin installed on here, then try again."
        cd $whereAmI
        exit 0
    fi
fi

cd ~/www
$adminCommand startproject $installName

# Now start placing template files.

sedCommand="sed 's/SHOWLOGSNAMEHERE/$installName/g'"

$sedCommand $fileLoc/basefiles/SHOWLOGSNAMEHERE.fcgi > ~/www/cgi-bin/$installName.fcgi
$sedCommand $fileLoc/basefiles/htaccess > ~/www/$installName/.htaccess

cp $fileLoc/basefiles/urls.py ~/www/$installName/$installName/.

if [ ! -d ~/www/$installName/showlog ]
then
    mkdir ~/www/$installName/showlog
    if [ $? -ne 0 ]
    then
        echo "That should have been possible..."
        echo "Where is ~/www/$installName?"
        cd $whereAmI
        exit 0
    fi
fi

cp -r $fileLoc/showlog/* ~/www/$installName/showlog/.

# Done!

cd $whereAmI
echo "Nothing seemed to break. Try out this url:"
echo "$USER.web.cern.ch/$USER/$installName"
