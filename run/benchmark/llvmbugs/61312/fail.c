int main() {
int a;
for (a = 2; a >= 0; a--)
;
unsigned b = -1 % a;
a = b;
if (a != 0)
__builtin_abort ();
return 0;
}