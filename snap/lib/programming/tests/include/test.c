
#include "snap.h"

int main(int argc, char** argv){

	int var = 80085;

	long int address = (long int)&var;

	int check_var = *(int*)address;

	printf("var %i\n", check_var);

	switch (address){
		default: printf("switch ok\n");
	}

	return 0;
}
