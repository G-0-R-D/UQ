# sudo apt-get install libgtk-3-dev
gcc gtk_gen_keymap.c `pkg-config --cflags --libs gtk+-3.0` -o gtk_gen_keymap
./gtk_gen_keymap

