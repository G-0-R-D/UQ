//#include <stdio.h>

int sum(int x, int y);

int main() {
	int x = 5, y=10; 
	
	sum(x,y);
	//printf("Sum of x and y is %d\n",sum(x, y));

	return 0;
}

int sum (int x , int y)
{
    return x+y; 
}

