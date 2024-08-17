static int a, *b[10][9];
int main() {
for (a = 0; a < 9; a++)
b[5][a] = b[a+1][4];
return 0;
}