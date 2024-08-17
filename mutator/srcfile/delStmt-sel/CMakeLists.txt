set(LLVM_LINK_COMPONENTS support)

add_clang_executable(delStmt-sel
  delStmt-sel.cpp
  )
target_link_libraries(delStmt-sel
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