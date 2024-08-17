set(LLVM_LINK_COMPONENTS support)

add_clang_executable(dupStmt-sel
  dupStmt-sel.cpp
  )
target_link_libraries(dupStmt-sel
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