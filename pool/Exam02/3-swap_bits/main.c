#include <stdio.h>
unsigned char swap_bits(unsigned char octet);
int main(void) {
    printf("%d\n", swap_bits(0));
    printf("%d\n", swap_bits(65));
    printf("%d\n", swap_bits(255));
    return 0;
}
