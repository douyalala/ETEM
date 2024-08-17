#include <stdint.h>
#include <stdio.h>
int32_t a;
int32_t b[10][1][9];
uint8_t c(int32_t *, uint64_t, uint32_t, int32_t d, int32_t *) { return d; }
int main() {
int e = 0, f=0, g=0;
int32_t *h = &b[0][0][3];
for (a = -23; a != -15; a = a + 2) {
int32_t *i = &b[0][0][3];
*i =
c(h, a, 0, b[0][0][3], &b[3][0][2]) ^ (-9L+0);
}
for (e = f = g = 0; g < 9; g++){
if (g == 3)
printf("%d\n", b[e][f][g]);
}
}