set(LLVM_LINK_COMPONENTS support)

add_clang_executable(moveStmt-sel
  moveStmt-sel.cpp
  )
target_link_libraries(moveStmt-sel
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