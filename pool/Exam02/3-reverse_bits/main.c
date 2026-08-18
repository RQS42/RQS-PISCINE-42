#include <stdio.h>
unsigned char reverse_bits(unsigned char octet);
int main(void) {
    printf("%d\n", reverse_bits(38));
    printf("%d\n", reverse_bits(255));
    printf("%d\n", reverse_bits(0));
    return 0;
}
