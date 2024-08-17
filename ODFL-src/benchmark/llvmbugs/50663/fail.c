int printf(const char *, ...);
static int c = 2, d;
short g, h;
int main() {
g ^= 50; // 50
c = 0 || g; // 1
h = g - 1; // 49
d = h & 1; // 1
c &= d; // 1
printf("c=%d,h=%d\n", c, h);
// CHECK-RESULT: c=1,h=49
return 0;
}