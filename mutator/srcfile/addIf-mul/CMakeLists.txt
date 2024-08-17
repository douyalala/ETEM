set(LLVM_LINK_COMPONENTS support)

add_clang_executable(addIf-mul
  addIf-mul.cpp
  )
target_link_libraries(addIf-mul
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