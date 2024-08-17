#include <stdio.h>
#include <stdarg.h>

void __attribute__((ms_abi)) Foo_va_list (int VaNum, const char  *Format, ...){
__builtin_ms_va_list  Marker;
long long    Value;

__builtin_ms_va_start (Marker, Format);
for (int i = 0; i < VaNum; i++ ) {
Value = __builtin_va_arg (Marker, int);
printf("Value = 0x%llx\n", Value);
}
__builtin_ms_va_end (Marker);
}

int main() {
Foo_va_list (16, "0123456789abcdef= %x%x%x%x%x%x%x%x%x%x%x%x%x%x%x%x\n",0,1,2,3,4,5,6,7,8,9,0xa,0xb,0xc,0xd,0xe,0xf);
return 0;
}