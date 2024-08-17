set(LLVM_LINK_COMPONENTS support)

add_clang_executable(repStmtFunction-mul
  repStmtFunction-mul.cpp
  )
target_link_libraries(repStmtFunction-mul
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