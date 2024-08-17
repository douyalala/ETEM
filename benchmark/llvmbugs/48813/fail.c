int printf (const char *, ...);

int c;
void d(unsigned f) { c = f; }

#pragma pack(1)
struct {
unsigned : 15;
signed : 21;
signed : 26;
signed a : 9;
} b;

int main() {
unsigned long e = b.a;
d(e >> 56);
printf("%d\n", c);
return 0;
}