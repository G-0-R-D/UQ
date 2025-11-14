export PKG_CONFIG_PATH=/home/user/.SETUP/install/lib/pkgconfig/
gcc test.c `pkg-config --cflags --libs sdl2` -o test
./test

