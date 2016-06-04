#!/bin/bash

# This is an installer used to install the ShowLogs webpage on your very own AFS space on lxplus.
# Yes, it only works there.
# This is in case you want me to make changes to my own page but I don't like you or something.

installName=$1

# I'm going to look for django here
# Feel free to change it, but it still has to be in your ~/www for the server I think

prefixLoc=$HOME/www/python_test/django

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

# Get the location of user and the template files before I wander off

whereAmI=`pwd`
fileLoc=`dirname $0`

# Initialize Django project.

cd ~/www

# Look for django installation

if [ ! -d $prefixLoc/lib/python2.6/site-packages ]
then

    # It needs to be installed in ~/www
    # This is mostly straight from the AFS page, so that should be safe, right?

    wget https://www.djangoproject.com/m/releases/1.6/Django-1.6.5.tar.gz
    tar -zxvf Django-1.6.5.tar.gz
    mv Django-1.6.5 django

    # Now I'm making up stuff
    cd django
    python2.6 setup.py install --prefix=$prefixLoc
    cd $prefixLoc
    wget https://pypi.python.org/packages/2.6/f/flup/flup-1.0.2-py2.6.egg
fi

# We'll need these for setup and to point the server to, but otherwise, you can forget them

PYTHONPATH=$prefixLoc/lib/python2.6/site-packages:$PYTHONPATH
PATH=$prefixLoc/bin:$PATH

adminCommand=`which django-admin.py`
if [ "$adminCommand" = "" ]
then
    adminCommand=`which django-admin`
fi
if [ "$adminCommand" = "" ]
then
    echo "This script did not work as I was expecting..."
    echo "Get django-admin installed on here, then try again."
    # This should really happen when I install django above
    cd $whereAmI
    exit 0
fi

cd ~/www

# This puts all sort of security keys and stuff that I don't want to show on GitHub,
# so we're installing from scratch sort of.

$adminCommand startproject $installName

# Now start placing template files.

cd $whereAmI

# Copy a couple of files with adjustments for user settings

sed "s@PROJECTNAMEHERE@$installName@g" $fileLoc/basefiles/fcgi_file.fcgi | sed "s@USERHOME@$HOME@g" | sed "s@DJANGOPREFIX@$prefixLoc/lib/python2.6/site-packages@g" | sed "s@FLUPLOCATION@$prefixLoc@g" > ~/www/cgi-bin/$installName.fcgi
chmod +x ~/www/cgi-bin/$installName.fcgi
sed "s@PROJECTNAMEHERE@$installName@g" $fileLoc/basefiles/htaccess > ~/www/$installName/.htaccess

# Place the urls file

cp $fileLoc/basefiles/urls.py ~/www/$installName/$installName/.

# Right now, we only have the showlog page, but let's make it

if [ ! -d ~/www/$installName/showlog ]
then
    mkdir ~/www/$installName/showlog
    if [ $? -ne 0 ]
    then
        echo "That should have been possible..."
        echo "Where is ~/www/$installName ???"
        cd $whereAmI
        exit 0
    fi
fi

cp -r $fileLoc/showlog/* ~/www/$installName/showlog/.

echo "Nothing seemed to break. Try out this url:"

# Again, only have showlog, which might change

echo "$USER.web.cern.ch/$USER/$installName/showlog"

# Done!
