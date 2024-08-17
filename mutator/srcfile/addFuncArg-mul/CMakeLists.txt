set(LLVM_LINK_COMPONENTS support)

add_clang_executable(addFuncArg-mul
  addFuncArg-mul.cpp
  )
target_link_libraries(addFuncArg-mul
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