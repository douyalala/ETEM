set(LLVM_LINK_COMPONENTS support)

add_clang_executable(delStmt-mul
  delStmt-mul.cpp
  )
target_link_libraries(delStmt-mul
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