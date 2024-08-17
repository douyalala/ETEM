int a, b = 30;
int main() {
unsigned c = 3;
for (a = 1; a; a--)
b = (-~c << b) * a;
b = -1 / ~-b;
return 0;
}