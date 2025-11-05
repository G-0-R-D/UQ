
py -B ../../include/snap/api/gen_args.py
gcc -I../../include -std=c89 test.c -o test
./test

