set(LLVM_LINK_COMPONENTS support)

add_clang_executable(moveStmt-mul
  moveStmt-mul.cpp
  )
target_link_libraries(moveStmt-mul
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