set(LLVM_LINK_COMPONENTS support)

add_clang_executable(delIf-mul
  delIf-mul.cpp
  )
target_link_libraries(delIf-mul
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