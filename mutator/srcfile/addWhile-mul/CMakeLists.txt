set(LLVM_LINK_COMPONENTS support)

add_clang_executable(addWhile-mul
  addWhile-mul.cpp
  )
target_link_libraries(addWhile-mul
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