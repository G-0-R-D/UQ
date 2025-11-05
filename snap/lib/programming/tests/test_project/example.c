// main.c

int sum(int a, int b) {
    return a + b;
}

int main(void) {
    if (sum(8, 10) < 20) {
        return -1;
    }
    return 1;
}

