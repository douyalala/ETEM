set(LLVM_LINK_COMPONENTS support)

add_clang_executable(add2If-mul
  add2If-mul.cpp
  )
target_link_libraries(add2If-mul
  PRIVATE
  clangAST
  clangASTMatchers
  clangBasic
  clangFrontend
  clangSerialization
  clangTooling
  clangDriver
  clangRewrite
  clangRewriteFrontend
  clangStaticAnalyzerFrontend
  clangToolingSyntax
  )