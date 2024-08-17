set(LLVM_LINK_COMPONENTS support)

add_clang_executable(repStmtFunction-sel
  repStmtFunction-sel.cpp
  )
target_link_libraries(repStmtFunction-sel
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