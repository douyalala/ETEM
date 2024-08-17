set(LLVM_LINK_COMPONENTS support)

add_clang_executable(addFunction-mul
  addFunction-mul.cpp
  )
target_link_libraries(addFunction-mul
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