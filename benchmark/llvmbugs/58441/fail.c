void printf();
int c;
int a(int b) {
int t = 0;
while (t < 7 && b) t++;
return t;
}
int e() {
int l;
for (l = 0; l < 6; l = l + 1)
for (c = 0; c < 6; c = (a(6) ^ 7) + c + 1)
;
}
int main() {
e();
printf("%d\n", c);
}